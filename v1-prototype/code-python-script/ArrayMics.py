from Mic import Mic
from PairMics import PairMics
import config
import numpy as np

class ArrayMics:
    """
    Manages an acoustic camera microphone array, combining pairwise cross-correlations 
    to generate spatial sound intensity maps via delay-and-sum beamforming and iterative CLEAN deconvolution.
    """

    def __init__(self, 
                 mics: list[Mic], 
                 grid: np.ndarray, 
                 smooth: float = config.SMOOTH,
                 focus_margin: float = config.FOCUS_MARGIN,
                 enable_focus: bool = False,
                 epsilon: float = config.EPSILON,
                 blob: float = config.BLOB,
                 clean_iter: int = 0,
                 clean_max: int = config.CLEAN_ITER_MAX,
                 decay: float = config.CLEAN_DECAY,
                 samples: int = config.AUDIO_SIZE): 
        """
        Initialize the array beamformer, setup microphone combinations, and pre-allocate beamforming buffers.

        Parameters:
            mics (list[Mic]): List of microphone node instances comprising the array.
            grid (np.ndarray): Target 3D coordinate projection grid of shape (H, W, 3).
            smooth (float): Exponential Moving Average (EMA) temporal smoothing factor [0.0, 1.0].
            focus_margin (float): Fraction of outer edge margin to zero out when spatial focus is enabled.
            enable_focus (bool): Toggle to zero-out border region noise around the grid frame.
            epsilon (float): Offset factor to avoid division-by-zero during normalization.
            blob (float): Threshold to strip away low-level sidelobe clutter ("blob control").
            clean_iter (int): Target iteration index to select from the CLEAN deconvolution cascade.
            clean_max (int): Maximum number of iterative CLEAN deconvolution passes to perform.
            decay (float): Subtraction factor per CLEAN iteration for dominant point-source cancellation.
            samples (int): Audio frame size in time-domain samples.
        """
        self.blob = blob
        self.smooth = smooth
        self.enable_focus = enable_focus
        self.clean_iter = clean_iter
        self.decay = decay

        self._epsilon = epsilon
        self._focus_margin = focus_margin
        
        # 1. Build unique PairMics combinations from all available microphones
        self._pairs = self._get_pair_combinations(mics, grid)
        
        # 2. Determine spatial frequency bounds averaged across all microphone pairs
        self.best_freq = self._get_avg_best_freq(self._pairs)
        
        # Pre-allocate intensity and temporal smoothing buffers
        self._intensity = np.zeros((clean_max + 1, grid.shape[0], grid.shape[1]))
        self._beamform_smooth = np.zeros((grid.shape[0], grid.shape[1], samples // 2))

    def get_beamform(self, bandpass: tuple[int, int]) -> np.ndarray:
        """
        Computes the acoustic intensity map over a given frequency band, applying temporal 
        smoothing, iterative CLEAN peak removal, logarithmic dynamic range compression, and normalization.

        Parameters:
            bandpass (tuple[int, int]): Low and high frequency bin indices (min_bin, max_bin).

        Returns:
            np.ndarray: Normalized 2D acoustic intensity heatmap matrix [0.0, 1.0] of shape (H, W).
        """
        # 1. Aggregate beamformed spatial coherence from all microphone pair combinations
        beamform = self._get_pairs_total(self._pairs, bandpass)
        
        # 2. Apply thresholding to suppress broad background noise/sidelobes
        beamform = self._apply_blob_control(beamform, self.blob)
        
        # 3. Apply IIR Exponential Moving Average (EMA) filter across time frames
        self._beamform_smooth[:, :, bandpass[0]:bandpass[1]] = self._get_smooth(
            self._beamform_smooth[:, :, bandpass[0]:bandpass[1]], beamform, self.smooth
        )

        beamform = self._beamform_smooth[:, :, bandpass[0]:bandpass[1]].copy()
        
        # 4. Integrate initial coherence across frequency channels to obtain base 2D intensity map
        self._intensity[0] = np.sum(beamform, axis=2)
        scale = np.max(beamform, axis=(0, 1)) + self._epsilon

        # 5. Perform iterative CLEAN algorithm to subtract dominant source point responses
        for i in range(1, self._intensity.shape[0]):
            # Locate spatial peak coordinates from previous iteration
            peak_y, peak_x = np.unravel_index(np.argmax(self._intensity[i - 1]), self._intensity[i - 1].shape)
            
            # Apply decay around peak location and attenuate frequency spectra
            scale, beamform = self._get_decay(beamform, (peak_y, peak_x), scale, self.decay)
            self._intensity[i] = np.sum(beamform, axis=2)

        # Select intensity state corresponding to desired clean iteration depth
        intensity = np.copy(self._intensity[self.clean_iter])
        
        # 6. Apply optional peripheral border zeroing
        if self.enable_focus:
            intensity = self._apply_focus(intensity, self._focus_margin)

        intensity = np.log(intensity+1)
        # 7. Normalize output to [0.0, 1.0]
        intensity /= (np.max(intensity) + self._epsilon)
        return intensity

    def _get_pairs_total(self, pairs: list[PairMics], bandpass: tuple[int, int]) -> np.ndarray:
        """Averages beamforming response across all active microphone pairs."""
        beamform = pairs[0].get_beamform(bandpass)
        for i in range(1, len(pairs)):
            beamform += pairs[i].get_beamform(bandpass)
        beamform /= len(pairs)
        return beamform

    def _get_pair_combinations(self, mics: list[Mic], grid: np.ndarray) -> list[PairMics]:
        """Generates all unique pairs C(N, 2) from a list of N microphone objects."""
        pairs = []
        for i in range(len(mics) - 1):
            for j in range(i + 1, len(mics)):
                pairs.append(PairMics(mics[i], mics[j], grid))
        return pairs

    def _get_avg_best_freq(self, pairs: list[PairMics]) -> tuple[int, int]:
        """Computes the mean optimal frequency bin range across all microphone pairs."""
        avg_min = 0.0
        avg_max = 0.0
        n = len(pairs)
        for p in pairs:
            best_freq = p.best_freq
            avg_min += best_freq[0] / n
            avg_max += best_freq[1] / n

        return (round(avg_min), round(avg_max))

    def _apply_blob_control(self, beamform: np.ndarray, blob: float) -> np.ndarray:
        """Clips acoustic coherence below a lower threshold and rescales remaining values."""
        result = np.maximum(beamform - blob, 0)
        result /= (1 - blob + self._epsilon)
        return result

    def _get_decay(self, beamform: np.ndarray, target: tuple[int, int], scale: np.ndarray, decay: float) -> tuple[np.ndarray, np.ndarray]:
        """Attenuates power spectra at a designated target pixel coordinate (CLEAN subtraction step)."""
        y, x = target
        # Calculate alignment factor based on peak spectrum contribution
        align = 1 - decay * (beamform[y, x, :] / (scale + self._epsilon))
        scale = scale * align
        beamform = beamform * align[np.newaxis, np.newaxis, :]
        return (scale, beamform)

    def _get_smooth(self, smooth_array: np.ndarray, instant_array: np.ndarray, smooth: float) -> np.ndarray:
        """Applies a first-order recursive Exponential Moving Average (EMA) filter across frames."""
        result = smooth * instant_array + (1 - smooth) * smooth_array
        return result

    def _apply_focus(self, intensity: np.ndarray, margin: float) -> np.ndarray: 
        """Zeros out peripheral frame margins to suppress boundary artifacts."""
        focus = np.copy(intensity)
        margin_x = int(focus.shape[1] * margin / 2)
        margin_y = int(focus.shape[0] * margin / 2)

        # Zero top, bottom, left, and right spatial margins
        focus[:margin_y, :] = 0          
        focus[-margin_y:, :] = 0         
        focus[:, :margin_x] = 0         
        focus[:, -margin_x:] = 0  

        return focus