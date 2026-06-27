import numpy as np

class ScannerGrid:
    """
    Maps every grid position to a 3D direction vector
    """

    def __init__(self, length: int, width: int, height:int , length_res: int, width_res: int):
        self.length = length
        self.width = width
        self.height = height
        self.length_res = length_res
        self.width_res = width_res

        self.length_units = np.linspace(-length/2, length/2, length_res)
        self.width_units = np.linspace(-width/2, width/2, width_res)

        self.length_size = len(self.length_units)
        self.width_size = len(self.width_units)

        grid_x = np.tile(self.width_units, self.length_size)
        grid_y = np.repeat(self.length_units, self.width_size)
        grid_z = np.repeat(height, self.length_size*self.width_size)

        dist = np.sqrt(grid_x**2 + grid_y**2 + grid_z**2)
        grid_x = grid_x/dist
        grid_y = grid_y/dist
        grid_z = grid_z/dist
        
        self.grid =  [grid_x, grid_y, grid_z]