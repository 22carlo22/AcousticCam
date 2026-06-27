from constants import FSAMPLE, VSOUND, SAMPLES, HALF_SAMPLE
import numpy as np
from Mic import Mic
from ScannerGrid import ScannerGrid

class PairMics:
    """
    Performs beamforming from a pair of microphones
    """
        
    def __init__(self, mic1: Mic, mic2: Mic, scanner: ScannerGrid, Nlow_const: int = 3, apply_bandpass: bool = True):
        self.mic1 = mic1
        self.mic2 = mic2
        self.scanner = scanner

        # Find the theoretical time delay for all possible sound source location
        dist_diff = (mic1.cord - mic2.cord) @ scanner.grid
        n0 = np.round(dist_diff * FSAMPLE / VSOUND)

        # Find the best frequencies to be detected
        max_n0 = np.max(np.abs(n0))
        self.Nhigh_max = int(np.round(SAMPLES / (4 * max_n0)))
        self.Nhigh = self.Nhigh_max
        self.Nlow = int(np.round(SAMPLES / ((4+Nlow_const) * max_n0)))

        # Calculate the theoretical phase shift from the time delay
        k = np.arange(HALF_SAMPLE)
        n0_col = n0.reshape(-1, 1) 
        self.phase_const = np.exp(-1j * 2 * np.pi * k * n0_col / SAMPLES)
        
        # Prepare the bandpass filter to capture the best frequencies 
        if apply_bandpass:
            self.bandpass = np.zeros(HALF_SAMPLE)
            self.bandpass[np.arange(self.Nlow, self.Nhigh)] = 1
        else:
            self.bandpass = np.ones(HALF_SAMPLE)


    def getBeamform(self):
        beamform = self.mic1.X_phase * np.conj(self.mic2.X_phase) * self.bandpass * self.phase_const
        return np.real(beamform)

    def getFreqRange(self) -> np.ndarray:
        return np.array([self.Nlow, self.Nhigh])