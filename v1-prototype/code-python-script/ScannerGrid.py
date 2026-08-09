import numpy as np
from config import HEATMAP_FLIP_ALONG_Y_AXIS, HEATMAP_FLIP_ALONG_X_AXIS

class ScannerGrid:
    """
    Constructs a spatial direction matrix mapping target camera pixel space to unit vectors.
    """
    def __init__(self, l, w, h, l_res, w_res, flip_l: bool = HEATMAP_FLIP_ALONG_Y_AXIS, flip_w: bool = HEATMAP_FLIP_ALONG_X_AXIS):
        """
        :param l: Physical horizontal FOV grid dimension in pixel-scaled coordinates.
        :param w: Physical vertical FOV grid dimension in pixel-scaled coordinates.
        :param h: Equivalent camera focal length in pixels.
        :param l_res: Horizontal grid point resolution.
        :param w_res: Vertical grid point resolution.
        :param flip_l: Invert horizontal spatial vectors if set.
        :param flip_w: Invert vertical spatial vectors if set.
        """
        l_units = np.linspace(-l/2, l/2, l_res) 
        w_units = np.linspace(-w/2, w/2, w_res)

        if flip_l: l_units *= -1
        if flip_w: w_units *= -1

        self.grid = np.zeros((len(w_units), len(l_units), 3))

        # Generate normalized unit direction vectors [X, Y, Z] for each target cell
        for y in range(self.grid.shape[0]):
            for x in range(self.grid.shape[1]):
                self.grid[y, x] = np.array([l_units[x], w_units[y], h]) / np.sqrt(w_units[y]**2 + l_units[x]**2 + h**2)