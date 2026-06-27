from UdpStreamServer import UdpStreamServer
import keyboard
import cv2
import queue
import time
import numpy as np
import matplotlib.pyplot as plt
from CalculateThread import CalculateThread
from SerialReaderThread import SerialReaderThread
from constants import FPS, SERVER_PORT

# Start the threads
serial_reader = SerialReaderThread()
calculator = CalculateThread(serial_reader.buffer_out)
stream = UdpStreamServer(ip="0.0.0.0", port=SERVER_PORT, max_buffers=4).start()
serial_reader.start()
calculator.start()


# Configure the plot
plt.ion()
fig, ax = plt.subplots()
dx = calculator.scanner.width / calculator.scanner.width_res
dy = calculator.scanner.length / calculator.scanner.length_res
img_extent = [
    -calculator.scanner.width/2 - dx/2, calculator.scanner.width/2 + dx/2,
    -calculator.scanner.length/2 - dy/2, calculator.scanner.length/2 + dy/2
]

frame = stream.frame_queue.get()
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
cam_img = ax.imshow(frame_rgb, extent=img_extent, zorder=1)

heatmap_img = ax.imshow(
    np.zeros((calculator.scanner.length_size, calculator.scanner.width_size, 4)), 
    origin='lower', 
    extent=img_extent,
    interpolation='gaussian', 
    aspect='equal',
    zorder=2
)
ax.invert_xaxis()


try:
    t = time.time()
    while True:
        if keyboard.is_pressed('q'):
            break
        
        # Display the video stream
        try:
            frame = stream.frame_queue.get(block=False)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cam_img.set_data(frame_rgb)
        except queue.Empty:
            pass

        # overlay heatmap 
        try:
            heatmap_pixels = calculator.buffer_out.get(block=False)
            heatmap_img.set_data(heatmap_pixels)
        except queue.Empty:
            pass

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        
        # Frame rate control
        to_delay = (1/FPS) - (time.time()-t)
        t = time.time()
        if(to_delay > 0):
            time.sleep(to_delay)
        
        
except Exception as e:
    print(f"Loop interrupted: {e}")

finally:
    plt.close('all') 
    stream.stop()
    calculator.stop()
    serial_reader.stop()
