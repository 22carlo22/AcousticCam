import queue
import threading
from constants import SAMPLES, SERIAL_PORT, REQ_AUDIO_DATA, BAUDRATE
import numpy as np
import serial

class SerialReaderThread:
    """
    Reads the incoming audio from esp via serial 
    """
    def __init__(self):
        self.s1 = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2)
        self.s1.reset_input_buffer()
        self.buffer_out = queue.Queue(maxsize = 2)
        self.expected_bytes = SAMPLES*4*4
        self.running = False
        
    def start(self):
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        while self.running:
            raw = []

            # Get the next audio chunk
            while len(raw) != self.expected_bytes:          # request again if it is corrupted                      
                self.s1.write(bytes([REQ_AUDIO_DATA]))             
                raw = self.s1.read(self.expected_bytes)
                
            data = np.frombuffer(raw, dtype=np.int32)
            self.buffer_out.put(data)
        self.s1.close()
            
    def stop(self):
        self.running = False