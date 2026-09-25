# ==========================================
# Network Communication
# ==========================================
SENDER_LOCAL_IP: str = "192.168.4.1"     # Local IP address of ESP32
AUDIO_PORT: int = 5010                   # Port for audio stream
CAM_PORT: int = 5011                     # Port for video stream

# ==========================================
# Camera 
# ==========================================
CAM_RESOLUTION_PIXELS: tuple[int, int] = (320, 240)  # Camera resolution in pixels (QVGA, OV2640 sensor)
CAM_SENSOR_WIDTH_MM: float = 3.52                     # Image sensor width (mm)
CAM_FOCAL_LEN_MM: float = 3.59                       # Lens focal length (mm)
CAM_FOCAL_PIX: float = CAM_RESOLUTION_PIXELS[0] * CAM_FOCAL_LEN_MM / CAM_SENSOR_WIDTH_MM # Focal length in pixel units


# ==========================================
# Audio 
# ==========================================
AUDIO_SAMPLING_RATE_HZ: int = 2 * 15000      # Sampling rate in Hz (INMP441 max bandwidth: 15 kHz -> Nyquist: 30 kHz)
AUDIO_SIZE: int = 2000                       # Samples per frame for beamforming; higher improves accuracy but lowers FPS
MIC_ARRAY_SIDE_LENGTH_M: float = 0.07        # Microphone array side length (meters)
SOUND_VELOCITY_MPS: float = 343              # Speed of sound in air at room temperature (m/s)

# ==========================================
# Beamforming Algorithm 
# ==========================================
SCANNER_QUALITY: float = 0.15                # Range: [0, 1]. Higher increases heatmap resolution but lowers FPS
SCANNER_FLIP_ALONG_X_AXIS: bool = True      # Flip heatmap horizontally if image is mirrored
SCANNER_FLIP_ALONG_Y_AXIS: bool = True      # Flip heatmap vertically if image is mirrored

HEATMAP_TRANSPARENT: float = 0.6            # Range: [0, 1]. Higher increases heatmap opacity

LOW_FREQ_CUTOFF: int = 5                    # FFT bin cutoff. Increasing detects lower frequencies but may enlarge "blobs"

SOURCE_DISTANCE_M: float = 1                # Range: > 0 meters. How far away the sound source being detected.

# ==========================================
# Slider UI Configurations
# ==========================================

# Heatmap jitter reduction
SMOOTH_MIN: float = 0.01                  # Range: [0, SMOOTH_MAX]
SMOOTH_MAX: float = 0.4                   # Range: [SMOOTH_MIN, 1]
SMOOTH: float = 0.1                       # Range: [SMOOTH_MIN, SMOOTH_MAX]. Higher reduces jitter

# CLEAN algorithm: removes dominant sound sources masking weaker ones
CLEAN_ITER_MAX: int = 5               # Range: > 0
CLEAN_ITER: int = 0                   # Range: [0, CLEAN_ITER_MAX]. Set 0 to disable CLEAN processing
CLEAN_DECAY: float = 0.9              # Range: [0, 1]. Higher aggressively removes dominant sources to reveal weaker ones

# Frequency blob suppression (helps isolate discrete sound sources)
BLOB_MIN: float = 0.8              # Range: [0, BLOB_MAX]
BLOB_MAX: float = 0.99             # Range: [BLOB_MIN, 1]
BLOB: float = 0.9                  # Range: [BLOB_MIN, BLOB_MAX]. Higher increases blob reduction

# Peak extraction (isolates dominant sound source)
PEAK_MIN: float = 0.5                     # Range: [0, PEAK_MAX]
PEAK_MAX: float = 0.99                    # Range: [PEAK_MIN, 1]
PEAK: float = 0.7                         # Range: [PEAK_MIN, PEAK_MAX]. Higher suppresses weaker sounds more aggressively

# Heatmap region isolation
FOCUS_ENABLE: bool = False         # Enable region of interest focus mode
FOCUS_MARGIN: float = 0.5          # Range: [0, 1]. Higher narrows the focus region

# ==========================================
# Other Constants & Helpers
# ==========================================
EPSILON: float = 10**-10                    # Small constant to prevent division by zero
TARGET_FPS: int = 20                        # Target frame rate; actual FPS depends on processing load

# Frequency conversion helpers (FFT bin index <-> Hz)
to_hz = lambda k: k * AUDIO_SAMPLING_RATE_HZ // AUDIO_SIZE      # Convert FFT bin index to Hz
to_k = lambda hz: hz * AUDIO_SIZE // AUDIO_SAMPLING_RATE_HZ     # Convert Hz to FFT bin index