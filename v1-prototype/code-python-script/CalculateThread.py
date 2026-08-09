import numpy as np
import threading
import queue
from config import ARRAY_MICS_SQUARE_LEN, SCANNER_QUALITY, CAM_RESOLUTION, FOCAL_PIX
from ScannerGrid import ScannerGrid
from Mic import Mic
from PairMics import PairMics
from Heatmap import Heatmap
from Bandpass import Bandpass

class CalculateThread:
    """
    Background worker thread handling real-time audio sample demuxing, windowing, 
    spectral filtering, multi-pair SRP-PHAT beamforming, and heatmap generation.
    """
    def __init__(self, buffer_in):
        """
        :param buffer_in: Multithreaded queue delivering raw interleaved multi-channel PCM byte arrays.
        """
        self.buffer_in = buffer_in
        self.buffer_out = queue.Queue(maxsize=2)

        # Construct spatial target direction grid based on camera parameters
        self.scanner = ScannerGrid(
            CAM_RESOLUTION[0], 
            CAM_RESOLUTION[1], 
            FOCAL_PIX, 
            CAM_RESOLUTION[0] // SCANNER_QUALITY, 
            CAM_RESOLUTION[1] // SCANNER_QUALITY
        )

        self.heatmap = Heatmap()

        # Physical 3D array layout coordinates [X, Y, Z] in meters for 4 planar mics
        self.m1 = Mic(np.array([0, 0, 0]))
        self.m2 = Mic(np.array([ARRAY_MICS_SQUARE_LEN, 0, 0]))
        self.m3 = Mic(np.array([0, ARRAY_MICS_SQUARE_LEN, 0]))
        self.m4 = Mic(np.array([ARRAY_MICS_SQUARE_LEN, ARRAY_MICS_SQUARE_LEN, 0]))

        # Instantiate 6 cross-correlation mic pairs across all combinations
        self.p1 = PairMics(self.m1, self.m2, self.scanner)
        self.p2 = PairMics(self.m1, self.m3, self.scanner)
        self.p3 = PairMics(self.m3, self.m4, self.scanner)
        self.p4 = PairMics(self.m4, self.m2, self.scanner)
        self.p5 = PairMics(self.m2, self.m3, self.scanner)
        self.p6 = PairMics(self.m4, self.m1, self.scanner)

        # Compute average un-aliased frequency passband across all pairs
        freq_ranges = np.array([
            self.p1.bestFreq, self.p2.bestFreq, self.p3.bestFreq, 
            self.p4.bestFreq, self.p5.bestFreq, self.p6.bestFreq
        ])
        avg_freq_range = np.average(freq_ranges, axis=0).astype(int)
        self.bandpass = Bandpass(avg_freq_range)
        
        self.running = False
    
    def start(self):
        """
        Starts background worker execution.
        """
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        return self
        
    def _run(self):
        """
        Main computational processing loop.
        """
        while self.running:            
            # Retrieve interleaved 4-channel audio frame from input buffer
            data = np.frombuffer(self.buffer_in.get(), dtype=np.int32)

            self.m1.putData(data[0::4])
            self.m2.putData(data[1::4])
            self.m3.putData(data[2::4])
            self.m4.putData(data[3::4])

            # Only process frequency bins within the computed bandpass range to avoid spatial aliasing
            filter = self.bandpass.get()
            result = (
                self.p1.getBeamform(filter) + self.p2.getBeamform(filter) + 
                self.p3.getBeamform(filter) + self.p4.getBeamform(filter) + 
                self.p5.getBeamform(filter) + self.p6.getBeamform(filter)
            ) / 6.0

            # Render sound localization heatmap RGBA frame
            location = self.heatmap.getLocationEachFreq(result)
            intensity = self.heatmap.getIntensity(location)
            rgba = self.heatmap.getRGBA(intensity)
            
            self.buffer_out.put(rgba)

    def stop(self):
        """
        Stops loop execution.
        """
        self.running = False