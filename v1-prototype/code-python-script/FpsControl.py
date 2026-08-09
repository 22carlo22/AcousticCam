import time
from config import FPS

class FpsControl:
    """
    Provides frame rate regulation and computes loop delay times in milliseconds.
    """
    def __init__(self, fps=FPS):
        """
        :param fps: Target frame rate cap.
        """
        self.t = time.time()
        self.target_frame_duration = 1.0 / fps

    def getDelayMs(self) -> int:
        """
        Calculates remaining sleep period required in milliseconds to maintain the target frame timing.
        
        :return: Delay duration in milliseconds (>= 0).
        """
        elapsed_seconds = time.time() - self.t
        delay = int((self.target_frame_duration - elapsed_seconds) * 1000)
        if delay <= 0:
            delay = 0
        self.t = time.time()
        return delay