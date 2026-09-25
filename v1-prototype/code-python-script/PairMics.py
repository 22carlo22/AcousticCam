import config
import numpy as np
from Mic import Mic

class PairMics:
    """
    Computes cross-spectral beamforming and Time Difference of Arrival (TDOA) 
    steering vectors for a microphone pair across a 3D target spatial grid.
    """

    def __init__(self, 
                 mic1: Mic, 
                 mic2: Mic, 
                 grid: np.ndarray,
                 fsample: int = config.AUDIO_SAMPLING_RATE_HZ,
                 vsound: float = config.SOUND_VELOCITY_MPS,
                 samples: int = config.AUDIO_SIZE,
                 freq_low_const: float = config.LOW_FREQ_CUTOFF):
        """
        Initialize microphone pair physical properties, sample parameters, and steering vectors.

        Parameters:
            mic1 (Mic): First microphone instance in the array pair.
            mic2 (Mic): Second microphone instance in the array pair.
            grid (np.ndarray): Target 3D spatial grid coordinates of shape (H, W, 3).
            fsample (int): Audio sampling frequency in Hz.
            vsound (float): Speed of sound propagation in m/s.
            samples (int): Total audio frame sample length.
            freq_low_const (float): Constant determining the lower bound cutoff for optimal frequency band selection.
        """
        self._fsample = fsample
        self._vsound = vsound
        self._samples = samples
        self._half_sample = samples // 2
        self._freq_low_const = freq_low_const

        self._mic1 = mic1
        self._mic2 = mic2

        # 1. Compute time delays (in sample units) for each point on the target grid
        n = self._get_time_delay(self._mic1.pos, self._mic2.pos, grid)
        
        # 2. Pre-calculate steering phase vectors and optimal frequency band limits
        self._expected_phase = self._get_steering_vector(n)
        self.best_freq = self._get_best_freq(n)

    def get_beamform(self, bandpass: tuple[int, int]) -> np.ndarray:
        """
        Computes spatial phase-alignment cross-correlation across specified frequency bins.

        Parameters:
            bandpass (tuple[int, int]): Low and high frequency bin indices (min_bin, max_bin).

        Returns:
            np.ndarray: Normalized phase coherence intensity response scaled to [0, 1].
        """
        # Calculate complex cross-spectral density (CSD) phase between mic signals: S1 * S2*
        cross_spectrum = self._mic1.phase * np.conj(self._mic2.phase)
        
        # Multiply CSD phase with theoretical delay phase shifts across selected frequency band
        beamform = cross_spectrum[np.newaxis, np.newaxis, bandpass[0] : bandpass[1]] * self._expected_phase[:, :, bandpass[0] : bandpass[1]]        
        
        # Extract real phase alignment and normalize cosine range [-1, 1] to probability range [0, 1]
        return (np.real(beamform) + 1) / 2

    def _get_time_delay(self, pos1: np.ndarray, pos2: np.ndarray, grid: np.ndarray) -> np.ndarray:
        """
        Computes TDOA (in sample units) between two microphones for all grid coordinates.

        Returns:
            np.ndarray: Matrix of shape (H, W) containing TDOA values in discrete sample units.
        """
        # 1. Calculate Euclidean distance vectors along spatial coordinate axis (axis=-1)
        dist1 = np.linalg.norm(grid - pos1, axis=-1)
        dist2 = np.linalg.norm(grid - pos2, axis=-1)

        # 2. Compute TDOA in samples across full spatial grid: delta_samples = (d2 - d1) / vsound * fsample
        return (dist2 - dist1) * (self._fsample / self._vsound)

    def _get_steering_vector(self, n: np.ndarray) -> np.ndarray:
        """
        Generates complex exponential phase shift steering matrix per spatial grid coordinate.

        Returns:
            np.ndarray: Complex matrix of shape (H, W, positive_frequency_bins).
        """
        k = np.arange(self._half_sample)
        # Phase shift formula: exp(-j * 2 * pi * delay_samples * bin_index / total_samples)
        return np.exp(-1j * 2 * np.pi * n[:, :, np.newaxis] * k / self._samples)

    def _get_best_freq(self, n: np.ndarray) -> tuple[int, int]:
        """
        Determines spatial anti-aliasing bounds (Nyquist-spatial cutoff) based on maximum delay.

        Returns:
            tuple[int, int]: Frequency bin index range (low_bin_index, high_bin_index).
        """
        max_n = np.max(np.abs(n))
        # Compute frequency bounds to avoid spatial phase wrapping (grating lobes)
        best_freq = (
            int(self._samples / ((2 + self._freq_low_const) * max_n)), 
            int(self._samples / (2 * max_n))
        )
        return best_freq