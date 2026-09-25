import numpy as np
import threading
import queue
import config
from ScannerGrid import ScannerGrid
from Mic import Mic
from ArrayMics import ArrayMics
from Heatmap import Heatmap
from SlidingAudio import SlidingAudio

class CalculateThread:
    """
    Asynchronous processing thread for acoustic camera calculation.
    
    Consumes raw multi-channel audio frames from an input queue, updates microphone 
    FFT buffers, performs array beamforming, converts power maps into RGBA heatmaps, 
    and publishes rendered frames to an output queue.
    """

    def __init__(self, buffer_in: queue.Queue):
        """
        Initialize the signal processing thread, spatial grid, microphone nodes, and command buffers.

        Parameters:
            buffer_in (queue.Queue): Thread-safe queue supplying raw interleaved audio byte frames.
        """
        self.buffer_in = buffer_in
        self.buffer_out = queue.Queue(maxsize=2)  # Output buffer holding rendered RGBA arrays (bounded to avoid lag)

        self.cmd_buffer = queue.Queue(maxsize=1)  # Command queue for runtime parameter adjustment

        # 1. Initialize projection grid based on camera sensor specs and quality factor
        self.scanner = ScannerGrid(
            config.CAM_RESOLUTION_PIXELS[0], 
            config.CAM_RESOLUTION_PIXELS[1], 
            config.CAM_FOCAL_PIX, 
            int(config.CAM_RESOLUTION_PIXELS[0] * config.SCANNER_QUALITY), 
            int(config.CAM_RESOLUTION_PIXELS[1] * config.SCANNER_QUALITY)
        )

        # 2. Instantiate 4-microphone planar square array (+X/+Y, -X/+Y, +X/-Y, -X/-Y)
        half_size = config.MIC_ARRAY_SIDE_LENGTH_M / 2
        self.m1 = Mic((half_size, half_size, 0))
        self.m2 = Mic((-half_size, half_size, 0))
        self.m3 = Mic((half_size, -half_size, 0))
        self.m4 = Mic((-half_size, -half_size, 0))

        # 3. Instantiate sliding circular buffer for 4 interleaved channels
        self.audio = SlidingAudio(4 * config.AUDIO_SIZE)

        # 4. Initialize beamforming array engine and RGBA heatmap renderer
        self.array_mics = ArrayMics([self.m1, self.m2, self.m3, self.m4], self.scanner.grid)
        self.heatmap = Heatmap()
        self.bandpass = self.array_mics.best_freq  # Initial frequency bin limits

        self.running = False
    
    def start(self):
        """
        Spawns and launches the background worker thread as a daemon process.

        Returns:
            CalculateThread: Self reference for method chaining.
        """
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        return self
        
    def _run(self):
        """
        Main worker loop: processes incoming IPC commands, ingests raw PCM data, 
        de-interleaves 4-channel audio, computes beamformed spatial intensity, and pushes RGBA heatmaps.
        """
        while self.running:            
            # Check for non-blocking parameter adjustment commands
            try:
                command = self.cmd_buffer.get(block=False)
                self._manage_cmd(command)
            except queue.Empty:
                pass

            # Ingest all available raw PCM chunks from the input buffer
            while self.buffer_in.qsize() > 0:
                data = np.frombuffer(self.buffer_in.get(), dtype=np.int32)
                self.audio.update(data)

            # De-interleave 4-channel audio data using stride slicing [channel_index::4]
            self.m1.update(self.audio.samples[0::4])
            self.m2.update(self.audio.samples[1::4])
            self.m3.update(self.audio.samples[2::4])
            self.m4.update(self.audio.samples[3::4])

            # Compute spatial beamforming intensity map across current frequency bandpass
            intensity = self.array_mics.get_beamform(self.bandpass)
            
            # Convert intensity field to RGBA heatmap frame and enqueue for display/GUI
            rgba = self.heatmap.getRGBA(intensity)
            self.buffer_out.put(rgba)

    class Command:
        """Data container holding a runtime configuration command string and value payload."""
        def __init__(self, cmd: str, arg):
            """
            Parameters:
                cmd (str): Command Identifier string (e.g. 'distance', 'bandpass', 'clean').
                arg (Any): Argument value corresponding to the command.
            """
            self.cmd = cmd
            self.arg = arg

    def _manage_cmd(self, command: Command):
        """
        Parses and dispatches runtime setting updates across array, scanner, and heatmap sub-modules.

        Parameters:
            command (Command): Incoming parameter update object.
        """
        cmd = command.cmd

        if cmd == "bandpass":
            self.bandpass = command.arg
        elif cmd == "clean":
            self.array_mics.clean_iter = command.arg
        elif cmd == "smooth":
            self.array_mics.smooth = command.arg
        elif cmd == "blob":
            self.array_mics.blob = command.arg
        elif cmd == "peak":
            self.heatmap.peak = command.arg
        elif cmd == "focus":
            self.array_mics.enable_focus = command.arg

    def stop(self):
        """
        Signals the calculation thread loop to terminate gracefully.
        """
        self.running = False