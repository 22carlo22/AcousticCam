import config
import numpy as np

class Mic:
    """
    Represents a single microphone node responsible for processing incoming 
    audio frame signals via Fast Fourier Transform (FFT).
    """

    def __init__(self, pos: tuple[float, float, float], samples=config.AUDIO_SIZE, epsilon=config.EPSILON):
        """
        Initialize microphone spatial properties and internal FFT buffers.

        Parameters:
            pos (tuple): 3D coordinates (x, y, z) of the microphone.
            samples (int): Total number of audio samples per frame.
            epsilon (float): Small offset to prevent division-by-zero during phase normalization.
        """
        # Store pre-calculated constants for fast slicing and windowing
        self._half_sample = samples // 2
        self._hamming = np.hamming(samples)  # Pre-computed Hamming window to reduce spectral leakage
        self._epsilon = epsilon

        # Spatial position vector
        self.pos = np.array(pos, dtype=float)

        # Output buffers holding the positive frequency components
        self.mag = np.zeros(self._half_sample, dtype=float)
        self.phase = np.zeros(self._half_sample, dtype=complex)

    def update(self, x: np.ndarray):
        """
        Process an incoming time-domain signal frame and update spectral magnitude and unit phase.

        Parameters:
            x (np.ndarray): 1D array of raw audio sample amplitudes.
        """

        x = x * self._hamming

        ft = np.fft.fft(x)[:self._half_sample] 

        self.mag = np.abs(ft)

        self.phase = ft / (self.mag + self._epsilon)