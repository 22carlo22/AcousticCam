from config import HEATMAP_SMOOTH, HEATMAP_BLOB, EPSILON, FOCUS_MARGIN, HEATMAP_TRANSPARENT, ENABLE_FOCUS
import numpy as np

class Heatmap:
    """
    Translates spatial beamforming energy matrices into temporal-smoothed, 
    threshold-filtered, color-mapped RGBA acoustic heatmaps.
    """
    def __init__(self):
        self.smooth = HEATMAP_SMOOTH
        self.blob = HEATMAP_BLOB
        self.focus_margin = FOCUS_MARGIN
        self.transparent = HEATMAP_TRANSPARENT
        self.enable_focus = ENABLE_FOCUS

    def getLocationEachFreq(self, X: np.ndarray) -> np.ndarray:
        """
        Applies a high-pass energy threshold cutoff per frequency bin to isolate peak acoustic sources.
        
        :param X: Raw steered response array across spatial grid [Y, X, Freq_Bins].
        :return: Scaled frequency response grid clipped below the blob threshold (values in [0, 1]).
        """
        loc = np.maximum(X - self.blob, 0)
        loc = loc / (1 - self.blob + EPSILON)
        return loc
        
    def getIntensity(self, X: np.ndarray) -> np.ndarray:
        """
        Integrates spatial energy across active frequency bins and updates an Exponential Moving Average (EMA) filter.
        
        :param X: Threshold-filtered spatial energy map across frequency bins.
        :return: Temporally smoothed 2D spatial intensity matrix.
        """
        # Integrate acoustic power across all selected frequency bins
        intensity = np.sum(X, axis=2)

        # Exponential Moving Average filter: I_smooth[t] = alpha * I[t] + (1 - alpha) * I_smooth[t-1]
        if not hasattr(self, 'intensity_smooth'):
            self.intensity_smooth = np.zeros_like(intensity)
        self.intensity_smooth = self.smooth * intensity + self.intensity_smooth * (1 - self.smooth)

        result = np.copy(self.intensity_smooth)
        if self.enable_focus: 
            result = self.applyFocus(result)

        # Allow logarithmic scaling for better visual contrast in low-intensity regions
        result = np.log10(result + 1)

        return result

    def applyFocus(self, intensity: np.ndarray) -> np.ndarray:
        """
        Zeroes out outer spatial margins to mask edge noise or off-axis boundary artifacts.
        
        :param intensity: 2D spatial sound intensity matrix.
        :return: Border-masked spatial intensity matrix.
        """
        margin_x = int(intensity.shape[1] * self.focus_margin / 2)
        margin_y = int(intensity.shape[0] * self.focus_margin / 2)

        intensity[:margin_y, :] = 0          
        intensity[-margin_y:, :] = 0         
        intensity[:, :margin_x] = 0         
        intensity[:, -margin_x:] = 0  

        return intensity

    def getRGBA(self, intensity: np.ndarray) -> np.ndarray:
        """
        Maps normalized spatial intensity levels to an explicit 4-stage color spectrum gradient:
        Transparent/Dark -> Blue -> Green -> Red -> White.
        
        :param intensity: Smoothed 2D spatial sound intensity map.
        :return: RGBA image matrix [Y, X, 4] with values normalized in [0.0, 1.0].
        """
        # Global normalization across spatial field
        intensity /= (np.max(intensity) + EPSILON)

        rgba = np.zeros((intensity.shape[0], intensity.shape[1], 4))

        # Color Region 1 [0.00 to 0.25]: Transparent / Dark to Blue
        mask1 = intensity < 0.25
        local1 = intensity[mask1] / 0.25
        rgba[mask1, 0] = 0          # Red
        rgba[mask1, 1] = 0          # Green
        rgba[mask1, 2] = local1     # Blue ramps up

        # Color Region 2 [0.25 to 0.50]: Blue to Cyan to Green
        mask2 = (0.25 <= intensity) & (intensity < 0.50)
        local2 = (intensity[mask2] - 0.25) / 0.25
        rgba[mask2, 0] = 0          # Red
        rgba[mask2, 1] = local2     # Green ramps up
        rgba[mask2, 2] = 1 - local2 # Blue ramps down

        # Color Region 3 [0.50 to 0.75]: Green to Yellow to Red
        mask3 = (0.50 <= intensity) & (intensity < 0.75)
        local3 = (intensity[mask3] - 0.50) / 0.25
        rgba[mask3, 0] = local3     # Red ramps up
        rgba[mask3, 1] = 1 - local3 # Green ramps down
        rgba[mask3, 2] = 0          # Blue

        # Color Region 4 [0.75 to 1.00]: Red to Peak White
        mask4 = (0.75 <= intensity) & (intensity <= 1.0)
        local4 = (intensity[mask4] - 0.75) / 0.25
        rgba[mask4, 0] = 1.0        # Red locked
        rgba[mask4, 1] = local4     # Green ramps up (Red + Green = Yellow -> White)
        rgba[mask4, 2] = local4     # Blue ramps up (RGB = White)

        # Map transparency proportional to intensity capped by global max alpha
        rgba[:, :, 3] = intensity * self.transparent

        return rgba