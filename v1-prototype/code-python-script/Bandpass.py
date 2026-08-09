from threading import Lock

class Bandpass:
    """
    Thread-safe container for active frequency bandpass limits (bin indices).
    Allows live dynamic updates from the GUI thread while being safely 
    read by the compute thread.
    """
    def __init__(self, freq_range):
        """
        :param freq_range: Initial [min_bin, max_bin] FFT index bounds.
        """
        self.lock = Lock() 
        self.freq_range = freq_range
    
    def update(self, freq_range): 
        """
        Updates the active frequency bin range.
        
        :param freq_range: New [min_bin, max_bin] FFT bin indices.
        """
        with self.lock:
            self.freq_range = freq_range
    
    def get(self):
        """
        Retrieves the current frequency bin range.
        
        :return: Current [min_bin, max_bin] FFT bin indices.
        """
        with self.lock:
            return self.freq_range