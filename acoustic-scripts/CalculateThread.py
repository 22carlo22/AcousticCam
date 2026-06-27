import numpy as np
import keyboard
import threading
import queue
from constants import FSAMPLE, SAMPLES, SCANNER_RATIO, SCANNER_WIDE, SCANNER_QUALITY
from enum import Enum, auto
from ScannerGrid import ScannerGrid
from Mic import Mic
from PairMics import PairMics
from NoiseFilter import NoiseFilter
from Heatmap import Heatmap

class CalculateThread:
    """
    Processes raw audio streams to generate a heatmap
    """

    class State(Enum):
        BEAMFORM = auto()
        NOISE_CALIBRATE = auto()
    
    def __init__(self, buffer_in):
        self.buffer_in = buffer_in
        self.buffer_out = queue.Queue(maxsize = 2)
        self.state = self.State.BEAMFORM

        # Setup standard look-grid matrix coordinates
        self.scanner = ScannerGrid(length=SCANNER_WIDE, width=SCANNER_WIDE*SCANNER_RATIO, height=1, length_res=SCANNER_QUALITY, width_res=SCANNER_QUALITY)
        self.hamming_window = np.hamming(SAMPLES)
        self.noiseFilter = NoiseFilter()
        self.heatmap = Heatmap(self.scanner)

        # Define coordinates (X, Y, Z) in meters for each of the 4 hardware microphones
        self.m1 = Mic(np.array([0, 0, 0]))
        self.m2 = Mic(np.array([-0.07, 0, 0]))
        self.m3 = Mic(np.array([0, -0.07, 0]))
        self.m4 = Mic(np.array([-0.07, -0.07, 0]))

        # Instantiate 6 cross-correlation pairs to find delays between all mic combinations
        self.p1 = PairMics(self.m1, self.m2, self.scanner, apply_bandpass = True)
        self.p2 = PairMics(self.m1, self.m3, self.scanner, apply_bandpass = True)
        self.p3 = PairMics(self.m3, self.m4, self.scanner, apply_bandpass = True)
        self.p4 = PairMics(self.m4, self.m2, self.scanner, apply_bandpass = True)
        self.p5 = PairMics(self.m2, self.m3, self.scanner, apply_bandpass = True)
        self.p6 = PairMics(self.m4, self.m1, self.scanner, apply_bandpass = True)

        # Print the frequencies that the pair of mics will detect
        freq_ranges = np.array([
            self.p1.getFreqRange(), 
            self.p2.getFreqRange(), 
            self.p3.getFreqRange(), 
            self.p4.getFreqRange(),
            self.p5.getFreqRange(),
            self.p6.getFreqRange()
        ])
        for i in range(6):
            hz = freq_ranges[i] *  (FSAMPLE / SAMPLES)
            print(f"Ear {i+1} -> Fmin: {hz[0]:.0f} Hz    Fmax: {hz[1]:.0f} Hz")

        self.running = False
    
    def start(self):
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        
    def _run(self):
        while self.running:

            # Read audio from serial
            data = self.buffer_in.get()
            self.m1.putData(data[0::4] * self.hamming_window)
            self.m2.putData(data[1::4] * self.hamming_window)
            self.m3.putData(data[2::4] * self.hamming_window)
            self.m4.putData(data[3::4] * self.hamming_window)

            # Find average power
            avg_power = (self.m1.X_mag**2 + self.m2.X_mag**2 + self.m3.X_mag**2 + self.m4.X_mag**2)/4

            # Remove background noise
            noise = self.noiseFilter.getNoiseIndex(avg_power)
            self.m1.removeNoise(noise)
            self.m2.removeNoise(noise)
            self.m3.removeNoise(noise)
            self.m4.removeNoise(noise)

            if self.state == self.State.BEAMFORM:
                # Locate the sound source
                result = self.p1.getBeamform() + self.p2.getBeamform() + self.p3.getBeamform() + self.p4.getBeamform() + self.p5.getBeamform() + self.p6.getBeamform()
                location = self.heatmap.getLocation(result)
                scaled = location * avg_power
                intensity =  self.heatmap.getIntensity(scaled)

                # Add color to the sound based on its loudness 
                rgba_buffer = self.heatmap.getLoudnessColor(intensity)
                self.buffer_out.put(rgba_buffer)

                # Trigger noise calibration manually with hotkey 'n'
                if keyboard.is_pressed('n'):
                    print("Noise vector is calibrating...")
                    self.state = self.State.NOISE_CALIBRATE
            
            elif self.state == self.State.NOISE_CALIBRATE:
                # Wait until the noise is fully captured
                if self.noiseFilter.calibrate(avg_power):
                    print("Noise vector updated!")
                    self.state = self.State.BEAMFORM

    def stop(self):
        self.running = False