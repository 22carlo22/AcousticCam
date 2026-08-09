"""
Global configuration constants and helper functions for the Acoustic Camera.
"""

# ==========================================
# Audio & Acoustic Settings
# ==========================================
FSAMPLE = 44100              # Audio sample rate (Hz)
SAMPLES = 1024               # Samples per frame window
VSOUND = 343                 # Speed of sound in air (m/s)
ARRAY_MICS_SQUARE_LEN = 0.07 # Microphone array side length (meters)

# Beamforming & Resolution
SCANNER_QUALITY = 5          # Grid resolution scaling (lower = higher resolution)
FREQ_LOW_CONST = 5           # Low-frequency cutoff factor for spatial aliasing (higher = lower cutoff)

# ==========================================
# Camera & Optics Settings
# ==========================================
CAM_RESOLUTION = [320, 240]  # Camera resolution [Width, Height] in pixels
SENSOR_WIDTH = 3.6           # Image sensor width (mm)
FOCAL_LEN = 3.59             # Lens focal length (mm)
FPS = 20                     # Processing frame rate (frames per second)

# ==========================================
# Network Communication
# ==========================================
SENDER_LOCAL_IP = "0.0.0.0"  # Local IP address to listen on
AUDIO_PORT = 5010            # UDP port for audio stream
CAM_PORT = 5011              # UDP port for video stream

# ==========================================
# Heatmap & Visual Overlay Settings
# ==========================================
HEATMAP_TRANSPARENT = 0.6    # Max opacity of the heatmap overlay (0.0 to 1.0)
HEATMAP_FLIP_ALONG_X_AXIS = False # Flip heatmap horizontally
HEATMAP_FLIP_ALONG_Y_AXIS = False # Flip heatmap vertically

# Focus & Boundary Masking
ENABLE_FOCUS = False         # Enable spatial focus cropping
FOCUS_MARGIN = 0.5           # Crop boundary fraction reserved for focus area (smaller = more aggressive cropping, 0.0 to 1.0)

# ==========================================
# Signal Filtering & Thresholds
# ==========================================
# Smoothing Filter
HEATMAP_SMOOTH = 0.1         # Moving average filter factor (0.0 to 1.0)
SMOOTH_MIN = 0.01            # Minimum allowed smoothing factor
SMOOTH_MAX = 0.3             # Maximum allowed smoothing factor

# Energy Blob Isolation
HEATMAP_BLOB = 0.98          # Intensity threshold for hotspot blobs (0.0 to 1.0)
BLOB_MIN = 0.90              # Minimum allowed threshold
BLOB_MAX = 0.99              # Maximum allowed threshold

# ==========================================
# Derived Constants & Helper Functions
# ==========================================
EPSILON = 10**-10            # Small offset to prevent division by zero
HALF_SAMPLE = SAMPLES // 2   # Number of Nyquist FFT bins

# Focal length converted to pixel units
FOCAL_PIX = CAM_RESOLUTION[0] * FOCAL_LEN / SENSOR_WIDTH 

# Frequency conversion helpers (FFT bin index <-> Hz)
to_hz = lambda n: n * FSAMPLE // SAMPLES     # Convert bin index to Hz
to_n0 = lambda hz: hz * SAMPLES // FSAMPLE   # Convert Hz to bin index