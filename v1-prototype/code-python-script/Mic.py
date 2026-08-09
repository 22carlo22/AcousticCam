from config import HALF_SAMPLE, EPSILON, SAMPLES
import numpy as np

class Mic:
    """
    Represents an individual physical microphone node in the array.
    Handles temporal windowing, Fast Fourier Transform (FFT), and Phase Transform (PHAT) normalization.
    """
    # Precompute Hamming window array: w[n] = 0.54 - 0.46 * cos(2*pi*n / (N-1))
    HAMMING_WINDOW = np.hamming(SAMPLES)

    def __init__(self, cord: np.ndarray):
        """
        :param cord: 3D spatial position vector [X, Y, Z] in meters relative to array origin.
        """
        self.cord = cord

    def putData(self, x: np.ndarray):
        """
        Applies windowing, computes positive-frequency FFT components, and extracts 
        normalized phase vectors for GCC-PHAT cross-correlation processing.
        
        :param x: Raw 1D PCM audio sample slice for single buffer window.
        """
        # Apply Hamming window to reduce spectral leakage across frame boundaries
        x_windowed = x * self.HAMMING_WINDOW
        
        # Compute 1D Discrete Fourier Transform and retain positive frequencies up to Nyquist limit
        self.ft = np.fft.fft(x_windowed)[:HALF_SAMPLE] 
        
        # Get the phase of each freqeuncy
        self.X_phase = self.ft / (np.abs(self.ft) + EPSILON)