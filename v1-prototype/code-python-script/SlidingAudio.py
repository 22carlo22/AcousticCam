import numpy as np

class SlidingAudio:
    """
    Manages a fixed-size FIFO (First-In, First-Out) rolling audio buffer.
    
    Continuously shifts older audio samples out to make room for incoming audio data frames.
    """

    def __init__(self, len_samples: int):
        """
        Initialize an empty circular audio buffer filled with zeros.

        Parameters:
            len_samples (int): Total number of audio samples maintained in the rolling buffer.
        """
        self.len_samples = len_samples
        # Pre-allocate fixed-length buffer for 32-bit integer PCM audio samples
        self.samples = np.zeros(self.len_samples, dtype=np.int32)

    def update(self, data: np.ndarray):
        """
        Appends new incoming audio samples to the buffer, sliding out older samples.

        Parameters:
            data (np.ndarray): Array-like object containing new time-domain audio samples.
        """
        data = np.asarray(data)
        n = len(data)
        
        if n >= self.len_samples:
            # Overwrite entire buffer with the most recent len_samples if incoming frame is too large
            self.samples[:] = data[-self.len_samples:]
        else:
            # Shift existing memory left by n slots (moving oldest data out of view)
            self.samples = np.roll(self.samples, -n)
            # Overwrite trailing end of buffer with incoming sample array
            self.samples[-n:] = data