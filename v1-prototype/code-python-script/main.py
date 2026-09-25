import queue
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Custom module imports for acoustic camera pipeline
from FpsControl import FpsControl
from RangeSlider import RangeSliderH
from TcpClient import TcpClient
from CalculateThread import CalculateThread
import config

# --- Initialize background network ingestion and DSP worker threads ---
# 1. Connect to ESP32 video stream (MJPEG over TCP)
cam_reader = TcpClient(config.SENDER_LOCAL_IP, config.CAM_PORT).start()

# 2. Connect to ESP32 multi-channel audio stream (unbounded queue depth to avoid audio drops)
audio_reader = TcpClient(config.SENDER_LOCAL_IP, config.AUDIO_PORT, max_buffers=-1).start()

# 3. Launch background acoustic beamforming calculation engine
calculator = CalculateThread(audio_reader.data_queue).start()


def decode_frame(data: bytes) -> np.ndarray:
    """Decodes raw JPEG byte buffer from camera socket into a OpenCV BGR image matrix.

    Args:
        data (bytes): JPEG encoded image bytes.

    Returns:
        np.ndarray: Decoded BGR image matrix, horizontally flipped for mirror view.
    """
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    frame = cv2.flip(frame, 1)  # Horizontal flip to mirror live preview
    return frame


# Synchronize and pre-fill frame buffers prior to entering the Tkinter event loop
frame = decode_frame(cam_reader.data_queue.get())
heatmap = calculator.buffer_out.get()
fps = FpsControl()

# --- Main Tkinter GUI Initialization ---
# Primary Control Window
root = tk.Tk()
root.title("Acoustic Camera Controls")

# Secondary Video Render Window
video_win = tk.Toplevel(root)
video_win.title("Acoustic Camera Feed")

# Container label for rendering live composite image buffers inside video_win
image_label = tk.Label(video_win)
image_label.pack()


def send_cmd(command: CalculateThread.Command):
    """Dispatches a non-blocking configuration command to the calculation thread.

    Purges any stale unprocessed command in the single-slot buffer before queuing 
    the newest setting update.

    Args:
        command (CalculateThread.Command): Command payload object holding parameter key and value.
    """
    try:
        calculator.cmd_buffer.get_nowait()
    except queue.Empty:
        pass

    calculator.cmd_buffer.put_nowait(command)


# -----------------------------------------------------------------------------
# Control Widget Callbacks & Declarations
# -----------------------------------------------------------------------------

# --- Bandpass Frequency Range Controls ---
def bandpass_set(*args):
    """Callback for dual-slider frequency selection. Converts Hz values to FFT bin indices."""
    min_val = int(low_var.get())
    max_val = int(high_var.get())
    cmd = CalculateThread.Command(
        "bandpass", (config.to_k(min_val), config.to_k(max_val))
    )
    send_cmd(cmd)


# DoubleVars track frequency range state in Hz
low_var = tk.DoubleVar(value=config.to_hz(calculator.bandpass[0]))
high_var = tk.DoubleVar(value=config.to_hz(calculator.bandpass[1]))
low_var.trace_add("write", bandpass_set)
high_var.trace_add("write", bandpass_set)

frequency_label = tk.Label(root, text="Frequency Range")
frequency_label.pack(anchor="w", padx=20, pady=10)

frequency_slider = RangeSliderH(
    root,
    [low_var, high_var],
    min_val=config.to_hz(calculator.bandpass[0]),
    max_val=config.to_hz(calculator.bandpass[1]),
    padX=40,
    digit_precision=".0f",
    suffix=" Hz",
    bgColor="#f0f0f0",
)
frequency_slider.pack(fill="x", padx=20)


# --- CLEAN Algorithm Iteration Controls ---
def clean_set(x):
    """Updates discrete CLEAN deconvolution iteration count."""
    discrete = round(float(x))

    if clean_slider.get() != discrete:
        clean_slider.set(discrete)

    clean_label.config(text=f"Clean: {discrete}")
    cmd = CalculateThread.Command("clean", discrete)
    send_cmd(cmd)


clean_label = tk.Label(root, text=f"Clean: {calculator.array_mics.clean_iter}")
clean_label.pack(anchor="w", padx=20, pady=10)
clean_slider = ttk.Scale(
    root, from_=0, to=config.CLEAN_ITER_MAX, orient="horizontal", command=clean_set
)
clean_slider.set(calculator.array_mics.clean_iter)
clean_slider.pack(fill="x", padx=20)


# --- Temporal Smoothing Controls ---
def smooth_set(x):
    """Dispatches EMA temporal smoothing weight update."""
    cmd = CalculateThread.Command("smooth", float(x))
    send_cmd(cmd)


smooth_label = tk.Label(root, text="Smooth")
smooth_label.pack(anchor="w", padx=20, pady=10)
smooth_slider = ttk.Scale(
    root,
    from_=config.SMOOTH_MIN,
    to=config.SMOOTH_MAX,
    orient="horizontal",
    command=smooth_set,
)
smooth_slider.set(calculator.array_mics.smooth)
smooth_slider.pack(fill="x", padx=20)


# --- Sidelobe Blob Control ---
def blob_set(x):
    """Dispatches lower noise suppression threshold update."""
    cmd = CalculateThread.Command("blob", float(x))
    send_cmd(cmd)


blob_label = tk.Label(root, text="Blob", pady=10)
blob_label.pack(anchor="w", padx=20)
blob_slider = ttk.Scale(
    root,
    from_=config.BLOB_MIN,
    to=config.BLOB_MAX,
    orient="horizontal",
    command=blob_set,
)
blob_slider.set(calculator.array_mics.blob)
blob_slider.pack(fill="x", padx=20)


# --- Heatmap Peak Sensitivity Controls ---
def peak_set(x):
    """Dispatches heatmap peak contrast offset update."""
    cmd = CalculateThread.Command("peak", float(x))
    send_cmd(cmd)


peak_label = tk.Label(root, text="Peak", pady=10)
peak_label.pack(anchor="w", padx=20)
peak_slider = ttk.Scale(
    root,
    from_=config.PEAK_MIN,
    to=config.PEAK_MAX,
    orient="horizontal",
    command=peak_set,
)
peak_slider.set(calculator.heatmap.peak)
peak_slider.pack(fill="x", padx=20)


# --- Spatial Border Focus Toggle ---
def focus_toggle():
    """Toggles peripheral border zeroing to eliminate edge artifacts."""
    cmd = CalculateThread.Command("focus", focus_var.get())
    send_cmd(cmd)


focus_var = tk.BooleanVar(value=calculator.array_mics.enable_focus)
focus_checkbox = ttk.Checkbutton(
    root, text="Enable Focus", variable=focus_var, command=focus_toggle
)
focus_checkbox.pack(anchor="w", padx=20, pady=10)


# -----------------------------------------------------------------------------
# Video Overlay & Real-Time Rendering Pipeline
# -----------------------------------------------------------------------------

def render_live_frame(camera_frame: np.ndarray, heatmap_rgba: np.ndarray) -> np.ndarray:
    """Resizes and alpha-blends RGBA acoustic heatmap onto the camera video frame.

    Args:
        camera_frame (np.ndarray): BGR image matrix from camera feed (H, W, 3).
        heatmap_rgba (np.ndarray): Normalized RGBA array from DSP calculation (H_heat, W_heat, 4).

    Returns:
        np.ndarray: Blended 8-bit BGR composite image array.
    """
    target_shape = (camera_frame.shape[1], camera_frame.shape[0])

    # Bicubic interpolation upsamples low-res acoustic grid to match camera frame resolution
    heatmap_rgba_resized = cv2.resize(
        heatmap_rgba,
        target_shape,
        interpolation=cv2.INTER_CUBIC,
    )

    # Separate color and alpha channel components
    heatmap_rgb = heatmap_rgba_resized[:, :, :3]
    alpha = heatmap_rgba_resized[:, :, 3:]

    # Convert RGB [0.0, 1.0] float tensor to OpenCV BGR [0.0, 255.0] float array
    heatmap_bgr = cv2.cvtColor(
        (heatmap_rgb * 255.0).astype(np.float32), cv2.COLOR_RGB2BGR
    )

    # Per-pixel alpha blending: Composite = (Heatmap * Alpha) + (Camera * (1 - Alpha))
    blended = (heatmap_bgr * alpha) + (
        camera_frame.astype(np.float32) * (1.0 - alpha)
    )

    # Clamp bounds and cast back to 8-bit unsigned integer
    return np.clip(blended, 0, 255).astype(np.uint8)


def update_loop():
    """Main UI thread loop handling non-blocking queue ingestion, rendering, and dynamic loop timing."""
    global frame, heatmap

    # Non-blocking fetch of latest JPEG camera frame
    try:
        jpeg_bytes = cam_reader.data_queue.get(block=False)
        frame = decode_frame(jpeg_bytes)
    except queue.Empty:
        pass

    # Non-blocking fetch of latest calculated spatial RGBA heatmap
    try:
        heatmap = calculator.buffer_out.get(block=False)
    except queue.Empty:
        pass

    # Blend acoustic spatial map over live video feed
    result = render_live_frame(frame, heatmap)
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

    # Convert image tensor to Tkinter-compatible PhotoImage reference
    img_pil = Image.fromarray(result_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    # Refresh label canvas and maintain garbage collection reference
    image_label.configure(image=img_tk)
    image_label.image = img_tk

    # Pace frame execution dynamically using target FPS delay
    delay_ms = max(1, int(fps.getDelayMs()))
    root.after(delay_ms, update_loop)


def on_close():
    """Teardown handler to gracefully stop threads and destroy windows on GUI exit."""
    root.destroy()
    cam_reader.stop()
    calculator.stop()
    audio_reader.stop()


# Bind window close protocols to teardown handler
root.protocol("WM_DELETE_WINDOW", on_close)
video_win.protocol("WM_DELETE_WINDOW", on_close)

# Launch initial recursive Tkinter event callback and start mainloop
root.after(0, update_loop)
root.mainloop()