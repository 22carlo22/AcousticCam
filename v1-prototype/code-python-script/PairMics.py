from config import FSAMPLE, VSOUND, SAMPLES, HALF_SAMPLE, FREQ_LOW_CONST
import numpy as np
from Mic import Mic
from ScannerGrid import ScannerGrid

class PairMics:
    """
    Models a cross-correlation pair of two microphones.
    Precomputes steering phase delays across the scanner spatial grid and calculates SRP-PHAT beamforming responses.
    """
    def __init__(self, mic1: Mic, mic2: Mic, scanner: ScannerGrid):
        """
        :param mic1: First physical Mic instance.
        :param mic2: Second physical Mic instance.
        :param scanner: ScannerGrid instance containing directional unit vectors.
        """
        self.mic1 = mic1
        self.mic2 = mic2
        self.scanner = scanner

        # Distance vector between the microphone pair: Δr = r1 - r2
        baseline_vector = mic1.cord - mic2.cord

        # Compute theoretical sample delay (tau * Fs) across all spatial grid unit vectors:
        # tau = (u_dir • Δr) / v_sound
        # n0 (samples) = tau * Fs
        n0 = np.dot(scanner.grid, baseline_vector) * FSAMPLE / VSOUND

        # Compute spatial aliasing limits based on maximum baseline delay across grid directions:
        # Spatial aliasing occurs when phase shift exceeds pi radians.
        max_n0 = np.max(np.abs(n0))
        self.bestFreq = [
            int(SAMPLES / ((2 + FREQ_LOW_CONST) * max_n0)), 
            int(SAMPLES / (2 * max_n0))
        ]

        # Precompute spatial steering phase shifts across all grid points and frequency bins:
        # Steering Phase Matrix: H(u, k) = exp(-j * 2 * pi * k * n0(u) / N)
        # where k is the FFT bin index, n0(u) is delay in samples, N is SAMPLES count.
        k = np.arange(HALF_SAMPLE)
        self.phase_const = np.exp(-1j * 2 * np.pi * np.multiply.outer(n0, k) / SAMPLES)

    def getBeamform(self, bandpass: np.ndarray = None) -> np.ndarray:
        """
        Calculates GCC-PHAT cross-power spectral density steered toward all spatial grid points.
        
        :param bandpass: [min_bin, max_bin] FFT bin slice indices.
        :return: Real component of steered response power across spatial grid cells and selected frequencies.
        """
        if bandpass is None:
            bandpass = np.array([0, HALF_SAMPLE])
            
        # Extract active frequency range for normalized phase vectors
        p1 = self.mic1.X_phase[bandpass[0] : bandpass[1]]
        p2 = self.mic2.X_phase[bandpass[0] : bandpass[1]]

        # Compute Normalized Generalized Cross-Correlation (GCC-PHAT):
        # G_phat(f) = X1_phase(f) * conj(X2_phase(f))
        cross_spectrum = p1 * np.conj(p2)

        # Multiply cross-spectrum by precomputed steering phase shifts across grid field:
        # S(u, f) = G_phat(f) * exp(-j * 2 * pi * f * tau(u))
        beamform = cross_spectrum[np.newaxis, np.newaxis, :] * self.phase_const[:, :, bandpass[0] : bandpass[1]]
        
        # Take real component corresponding to phase alignment / constructive interference
        return np.real(beamform)