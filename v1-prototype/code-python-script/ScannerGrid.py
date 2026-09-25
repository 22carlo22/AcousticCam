import numpy as np
import config

class ScannerGrid:
    """
    Generates and manages a 3D target projection grid for a camera/scanner model.

    Projects a defined 2D image/sensor plane across a focal distance (h) to 
    determine corresponding 3D physical coordinates at a target distance.
    """

    def __init__(self, 
                 length: float, 
                 width: float, 
                 h: float, 
                 length_res: int, 
                 width_res: int, 
                 dist: float = config.SOURCE_DISTANCE_M, 
                 flip_length: bool = config.SCANNER_FLIP_ALONG_Y_AXIS, 
                 flip_width: bool = config.SCANNER_FLIP_ALONG_X_AXIS):
        """
        Initialize the scanner grid dimensions, resolution, and spatial orientation.

        Parameters:
            length (float): Physical length of the sensor plane along the X-axis.
            width (float): Physical width of the sensor plane along the Y-axis.
            h (float): Focal length or sensor offset distance.
            length_res (int): Number of grid points along the length (X-axis).
            width_res (int): Number of grid points along the width (Y-axis).
            dist (float): Target projection distance along the Z-axis.
            flip_length (bool): If True, reverses the directional orientation along the X-axis.
            flip_width (bool): If True, reverses the directional orientation along the Y-axis.
        """
        # 1. Generate 1D centered axis coordinate ranges
        length_range = np.linspace(-length / 2, length / 2, length_res)
        width_range = np.linspace(-width / 2, width / 2, width_res)

        # Handle axis direction flips for coordinate system alignment
        if flip_length:
            length_range = length_range[::-1]
        if flip_width:
            width_range = width_range[::-1]

        # 2. Generate and store 2D spatial coordinate meshes
        self._X, self._Y = np.meshgrid(length_range, width_range)
        self._h = h
        self.dist = dist

        # 3. Compute 3D coordinate projection at target distance
        scale = self.dist / self._h

        grid_x = self._X * scale
        grid_y = self._Y * scale
        grid_z = np.full_like(self._X, self.dist)

        # Stack into shape (H, W, 3) holding cartesian (X, Y, Z) vectors
        self.grid = np.stack([grid_x, grid_y, grid_z], axis=-1)