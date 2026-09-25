import time
import config

class FpsControl:
    """Provides frame rate regulation and computes loop delay times in milliseconds.

    Tracks frame execution time to ensure smooth frame pacing and prevent UI or 
    rendering loops from over-consuming hardware resources.
    """

    def __init__(self, fps: int = config.TARGET_FPS):
        """Initializes timer tracking state and computes target frame period.

        Args:
            fps (int): Target frame rate cap in Frames Per Second (FPS).
        """
        # Record initial frame start timestamp in seconds
        self.t = time.time()
        
        # Calculate maximum allowed frame duration (e.g., 1/60s = ~0.0166s per frame)
        self.target_frame_duration = 1.0 / fps

    def getDelayMs(self) -> int:
        """Calculates remaining sleep period required in milliseconds to maintain target FPS.

        Measures total elapsed processing time since the last frame call, subtracts 
        it from the frame period target, and updates the timestamp benchmark.

        Returns:
            int: Remaining delay time in milliseconds (clamped to >= 0).
        """
        # Calculate processing time consumed since the start of the current frame
        elapsed_seconds = time.time() - self.t
        
        # Determine remaining frame budget and convert from seconds to milliseconds
        delay = int((self.target_frame_duration - elapsed_seconds) * 1000)
        
        # Clamp negative delays to 0 ms (occurs if processing exceeded target frame duration)
        if delay <= 0:
            delay = 0
            
        # Benchmark start of the next frame cycle
        self.t = time.time()
        return delay