SAMPLES = 1024                  # Number of audio data points per frame 
VSOUND = 343                    # Speed of sound in m/s
FSAMPLE = 44100                 # Audio sampling rate in Hz 
EPSILON = 10**-10           
HALF_SAMPLE = SAMPLES // 2      # Number of unique frequency bins

SERIAL_PORT = 'COM13'           # The USB COM port for listeing incoming audio 
BAUDRATE = 921600  
REQ_AUDIO_DATA = 0              # Request command for the next audio chunk  

SERVER_PORT = 5005              # The network UDP port for listening incoming camera video frames
FPS = 10                        # Target refresh rate for the Matplotlib visualization window

SCANNER_WIDE = 0.7              # FOV of the beamform
SCANNER_RATIO = 320/240         # Dimension ratio of the video stream (ie. QVGA)
SCANNER_QUALITY = 10            # Affects the resolution of the heatmap

HEATMAP_TRANSPARENT = 0.7 
HEATMAP_SMOOTH = 0.1            # Lower value -> smoother effect; heatmap will focus more on stable sounds
