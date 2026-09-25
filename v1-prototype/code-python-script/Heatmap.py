import config 
import numpy as np

class Heatmap:
    """
    Transforms 2D normalized intensity matrices into 4-channel RGBA heatmaps.
    
    Applies peak contrast thresholding and maps scalar values to a custom color 
    gradient (Transparent -> Blue -> Green -> Red -> White).
    """

    def __init__(self, 
                 peak: float = config.PEAK, 
                 transparent: float = config.HEATMAP_TRANSPARENT, 
                 epsilon: float = config.EPSILON):
        """
        Initialize the heatmap colormap parameters.

        Parameters:
            peak (float): Minimum normalized intensity threshold (0.0 to 1.0) required to show color.
            transparent (float): Global scaling factor for the alpha channel (0.0 = invisible, 1.0 = fully opaque).
            epsilon (float): Small floating-point value to avoid division-by-zero errors.
        """
        self.peak = peak 
        self._transparent = transparent 
        self._epsilon = epsilon

    def _amplify_peaks(self, intensity: np.ndarray, peak: float) -> np.ndarray:
        """
        Clips background noise below the peak threshold and rescales remaining values to [0.0, 1.0].

        Parameters:
            intensity (np.ndarray): Normalized 2D acoustic intensity field.
            peak (float): Lower intensity threshold cut-off.

        Returns:
            np.ndarray: Amplified intensity array zeroed below `peak` and scaled to [0.0, 1.0].
        """
        # Zero out background values below peak threshold
        result = np.maximum(intensity - peak, 0)
        
        # Rescale the remaining range [peak, 1.0] back to full normalized range [0.0, 1.0]
        result /= (1 - peak + self._epsilon)
        return result

    def getRGBA(self, intensity: np.ndarray) -> np.ndarray:
        """
        Maps a 2D scalar intensity matrix into an RGBA color image tensor.

        Parameters:
            intensity (np.ndarray): 2D floating-point matrix of intensity values.

        Returns:
            np.ndarray: 3D array of shape (H, W, 4) containing normalized RGBA color values [0.0, 1.0].
        """
        # Apply non-linear dynamic range amplification
        intensity = self._amplify_peaks(intensity, self.peak)

        # Allocate empty 4-channel RGBA tensor (Height, Width, 4)
        rgba = np.zeros((intensity.shape[0], intensity.shape[1], 4))

        # Color Region 1 [0.00 to 0.25]: Black/Dark -> Pure Blue
        mask1 = intensity < 0.25
        local1 = intensity[mask1] / 0.25
        rgba[mask1, 0] = 0          # Red off
        rgba[mask1, 1] = 0          # Green off
        rgba[mask1, 2] = local1     # Blue ramps up [0.0 -> 1.0]

        # Color Region 2 [0.25 to 0.50]: Blue -> Cyan -> Pure Green
        mask2 = (0.25 <= intensity) & (intensity < 0.50)
        local2 = (intensity[mask2] - 0.25) / 0.25
        rgba[mask2, 0] = 0          # Red off
        rgba[mask2, 1] = local2     # Green ramps up [0.0 -> 1.0]
        rgba[mask2, 2] = 1 - local2 # Blue ramps down [1.0 -> 0.0]

        # Color Region 3 [0.50 to 0.75]: Green -> Yellow -> Pure Red
        mask3 = (0.50 <= intensity) & (intensity < 0.75)
        local3 = (intensity[mask3] - 0.50) / 0.25
        rgba[mask3, 0] = local3     # Red ramps up [0.0 -> 1.0]
        rgba[mask3, 1] = 1 - local3 # Green ramps down [1.0 -> 0.0]
        rgba[mask3, 2] = 0          # Blue off

        # Color Region 4 [0.75 to 1.00]: Red -> Peak White
        mask4 = (0.75 <= intensity) & (intensity <= 1.0)
        local4 = (intensity[mask4] - 0.75) / 0.25
        rgba[mask4, 0] = 1.0        # Red locked at full brightness
        rgba[mask4, 1] = local4     # Green ramps up [0.0 -> 1.0]
        rgba[mask4, 2] = local4     # Blue ramps up [0.0 -> 1.0] (R=1, G=1, B=1 creates White)

        # Map transparency proportional to intensity, capped by max alpha factor
        rgba[:, :, 3] = intensity * self._transparent

        return rgba