import cv2
import queue
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from RangeSlider import RangeSliderH

from CalculateThread import CalculateThread
from config import CAM_PORT, AUDIO_PORT, SMOOTH_MAX, SMOOTH_MIN, BLOB_MAX, BLOB_MIN, SENDER_LOCAL_IP, to_hz, to_n0
from Udp import Udp
from FpsControl import FpsControl 

# --- Initialize background network ingestion and DSP threads ---
cam_reader = Udp(SENDER_LOCAL_IP, CAM_PORT).start()
audio_reader = Udp(SENDER_LOCAL_IP, AUDIO_PORT).start()
calculator = CalculateThread(audio_reader.data_queue).start()

# Sync frame data buffers prior to loop startup
frame = cam_reader.data_queue.get()
heatmap = calculator.buffer_out.get()
fps = FpsControl()

# --- Setup Tkinter GUI Base Window ---
root = tk.Tk()
root.title("Acoustic Camera Controls & Feed")

# Video frame display container
image_label = tk.Label(root)
image_label.pack()

# --- Dynamic Parameter Callbacks & Observer Bindings ---
low_var = tk.DoubleVar(value=to_hz(calculator.bandpass.freq_range[0]))
high_var = tk.DoubleVar(value=to_hz(calculator.bandpass.freq_range[1]))

def bandpass_set(*args):
    """Callback to update active frequency bandpass bounds in computation thread."""
    min_val = int(low_var.get())
    max_val = int(high_var.get())
    calculator.bandpass.update([to_n0(min_val), to_n0(max_val)])

low_var.trace_add("write", bandpass_set)
high_var.trace_add("write", bandpass_set)

def smooth_set(x):
    """Callback to update temporal EMA smoothing coefficient."""
    calculator.heatmap.smooth = float(x)

def blob_set(x):
    """Callback to update heatmap noise threshold filter level."""
    calculator.heatmap.blob = float(x)

def focus_toggle():
    """Callback to toggle edge margin focus masking."""
    calculator.heatmap.enable_focus = focus_var.get()

# --- Build Control Interface Widgets ---
frequency_label = tk.Label(root, text="Frequency Range")
frequency_label.pack(anchor="w", padx=20, pady=10)

frequency_slider = RangeSliderH(
    root, 
    [low_var, high_var], 
    min_val=to_hz(calculator.bandpass.freq_range[0]), 
    max_val=to_hz(calculator.bandpass.freq_range[1]), 
    padX=40,
    digit_precision=".0f",
    suffix=" Hz",
    bgColor="#f0f0f0"
)
frequency_slider.pack(fill="x", padx=20)

smooth_label = tk.Label(root, text="Smooth")
smooth_label.pack(anchor="w", padx=20, pady=10)
smooth_slider = ttk.Scale(root, from_=SMOOTH_MIN, to=SMOOTH_MAX, orient="horizontal", command=smooth_set)
smooth_slider.set(calculator.heatmap.smooth)
smooth_slider.pack(fill="x", padx=20)

blob_label = tk.Label(root, text="Blob", pady=10)
blob_label.pack(anchor="w", padx=20)
blob_slider = ttk.Scale(root, from_=BLOB_MIN, to=BLOB_MAX, orient="horizontal", command=blob_set)
blob_slider.set(calculator.heatmap.blob)
blob_slider.pack(fill="x", padx=20)

focus_var = tk.BooleanVar(value=calculator.heatmap.enable_focus) 
focus_checkbox = ttk.Checkbutton(
    root, 
    text="Enable Focus", 
    variable=focus_var, 
    command=focus_toggle
)
focus_checkbox.pack(anchor="w", padx=20, pady=10)

# --- Real-Time Video Overlay and Pipeline Loop ---

def render_live_frame(camera_frame: np.ndarray, heatmap_rgba: np.ndarray) -> np.ndarray:
    """
    Alpha-blends the acoustic RGBA heatmap layer over the camera frame.
    
    Blend equation: Final = (Heatmap_RGB * Alpha) + (Camera_BGR * (1 - Alpha))
    
    :param camera_frame: Raw camera frame in OpenCV BGR format.
    :param heatmap_rgba: Calculated heatmap RGBA overlay frame.
    :return: Blended composite image matrix in uint8 BGR format.
    """
    # Interpolate low-res spatial grid up to match optical camera frame dimensions
    heatmap_rgba = cv2.resize(heatmap_rgba, (camera_frame.shape[1], camera_frame.shape[0]), interpolation=cv2.INTER_LINEAR)

    heatmap_rgb = heatmap_rgba[:, :, :3]
    alpha = heatmap_rgba[:, :, 3:] 

    # Convert normalized floating-point RGB to standard OpenCV 8-bit BGR scale
    heatmap_bgr = cv2.cvtColor((heatmap_rgb * 255.0).astype(np.float32), cv2.COLOR_RGB2BGR)
    
    # Perform per-pixel alpha blending
    blended = (heatmap_bgr * alpha) + (camera_frame.astype(np.float32) * (1.0 - alpha))

    return np.clip(blended, 0, 255).astype(np.uint8)

def update_loop():
    """Main UI thread execution loop handling frame fetching, rendering, and dynamic pacing."""
    global frame, heatmap
    
    # Non-blocking fetch of latest JPEG camera frame
    try:
        jpeg_bytes = cam_reader.data_queue.get(block=False)
        frame = cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.flip(frame, 1) # Mirror preview horizontally for natural interaction
    except queue.Empty:
        pass

    # Non-blocking fetch of latest computed spatial heatmap RGBA frame
    try:
        heatmap = calculator.buffer_out.get(block=False)
    except queue.Empty:
        pass

    # Overlay acoustic spatial data on video feed and refresh Tkinter Canvas
    result = render_live_frame(frame, heatmap)
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    
    img_pil = Image.fromarray(result_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    
    image_label.configure(image=img_tk)
    image_label.image = img_tk  

    # Pacing UI loop step according to frame timing target
    delay_ms = max(1, int(fps.getDelayMs()))
    root.after(delay_ms, update_loop)

def on_close():
    """Clean thread teardown handler triggered on GUI close signal."""
    root.destroy()
    cam_reader.stop()
    calculator.stop()
    audio_reader.stop()

root.protocol("WM_DELETE_WINDOW", on_close)
root.after(0, update_loop)
root.mainloop()