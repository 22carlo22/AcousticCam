from constants import HALF_SAMPLE
import time
import numpy as np


class NoiseFilter:
    """
    Manages background noise floor estimation
    """
    def __init__(self, alpha: float = 0.2, noise_const: int = 5, dur: int = 10):
        self.alpha = alpha
        self.noise_const = noise_const
        self.is_calibrating = False
        self.dur = dur

        try:            
            self.noise = np.load("power_noise.npy")
        except FileNotFoundError:
            self.noise = np.zeros(HALF_SAMPLE)
        
    def getNoiseIndex(self, power: np.ndarray) -> np.ndarray:
        return (power - self.noise) < 0

    def calibrate(self, power: np.ndarray) -> bool:
        if(self.is_calibrating):
            # Gradually estimate the noise floor via EMA
            self.baseline = (1 - self.alpha) * self.baseline + self.alpha * power

            # and once a specified time has elapsed, save it as the actual noise
            if(time.time()-self.t > self.dur):
                self.noise = self.noise_const * self.baseline
                np.save("power_noise.npy", self.noise)
                self.is_calibrating = False
                return True
        else:
            self.t = time.time()
            self.baseline = np.zeros(HALF_SAMPLE)
            self.is_calibrating = True

        return False