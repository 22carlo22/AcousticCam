from constants import HALF_SAMPLE, EPSILON
import numpy as np


class Mic:
    """
    Calculates the magnitude and phase spectrum of an audio channel
    """
    def __init__(self, cord: np.ndarray):
        self.cord = cord

    def putData(self, x: np.ndarray):
        self.ft = np.fft.fft(x)[:HALF_SAMPLE]
        self.X_mag = np.abs(self.ft)
        self.X_phase =  self.ft / (self.X_mag+EPSILON)

    def removeNoise(self, noise: np.ndarray):
        self.X_mag[noise] = 0
        self.X_phase[noise] = 0