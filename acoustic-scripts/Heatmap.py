from constants import EPSILON, HEATMAP_SMOOTH, HEATMAP_TRANSPARENT
import numpy as np
from ScannerGrid import ScannerGrid

class Heatmap:
    """
    Generates the heatmap. Also, removes any possible sound artifacts.
    """
    def __init__(self, scanner: ScannerGrid, blob: float = 0.95):
        self.blob = blob
        self.scanner = scanner

    def getLocation(self, X: np.ndarray) -> np.ndarray:
        # Get only the constructive interference
        loc = np.maximum(X, 0)
        loc = loc / (np.max(loc, axis=0) + EPSILON)
        loc = np.maximum(loc - self.blob, 0)
        loc = loc / (1-self.blob)
        
        # Remove sounds outside of the field of view
        max_indices = np.argmax(loc, axis=0)
        max_indices_row = max_indices % self.scanner.width_size
        at_edges = (
            (0 <= max_indices) & (max_indices < self.scanner.width_size) | 
            (len(loc) - self.scanner.width_size <= max_indices) & (max_indices < len(loc)) | 
            (max_indices_row  == 0) | 
            (self.scanner.width_size-1 == max_indices_row)
        )
        sound_at_front = np.where(at_edges, 0, 1)
        loc = loc*sound_at_front
        
        return loc

    def getIntensity(self, X: np.ndarray) -> np.ndarray:
        # Sum up energy across all frequencies to get total sound intensity
        intensity = np.sum(X, axis=1)
        intensity = intensity / (np.max(intensity) + EPSILON)
        return intensity

    def getLoudnessColor(self, intensity: np.ndarray, alpha: float = HEATMAP_SMOOTH) -> np.ndarray:
        if hasattr(self, 'intensity_smooth') == False:
            self.intensity_smooth = np.zeros_like(intensity)
        self.intensity_smooth = alpha*intensity + self.intensity_smooth*(1-alpha)
        intensity = self.intensity_smooth

        colors = np.zeros((len(intensity), 3))

        # Quiet sound -> white
        mask = intensity < 0.2
        local = intensity[mask] / 0.2
        colors[mask] = np.stack([1-local, 1-local, np.ones_like(local)], axis = 1)

        mask = (0.2 <= intensity) & (intensity < 0.45)
        local = (intensity[mask]-0.2) / 0.25
        colors[mask] = np.stack([np.zeros_like(local), local, 1-local], axis = 1)

        mask = (0.45 <= intensity) & (intensity < 0.75)
        local = (intensity[mask]-0.45) / 0.3
        colors[mask] = np.stack([local, 1-local, np.zeros_like(local)], axis = 1)

        # Loud sound -> purple
        mask = (0.75 <= intensity) & (intensity <= 1)
        local = (intensity[mask]-0.75) / 0.25
        colors[mask] = np.stack([np.ones_like(local), np.zeros_like(local), local], axis = 1)

        rgba_buffer = np.zeros((len(intensity), 4))
        rgba_buffer[:, :3] = colors
        rgba_buffer[intensity > 0.05, 3] = HEATMAP_TRANSPARENT
        rgba_buffer = rgba_buffer.reshape(self.scanner.length_size, self.scanner.width_size, 4)
        return rgba_buffer
