# Purpose
This ESP32 handles three main tasks:
- Audio: Reads and synchronizes 4 microphones.
- Video: Continuously captures JPEG images from the OV3660 camera.
- Data Transfer: Streams the raw audio and image data to a connected device wirelessly.

<img width="445" height="512" alt="unnamed (5)" src="https://github.com/user-attachments/assets/15dba30b-47f7-49e4-b1cd-c952ad9015ec" />

# Parts

1. Freenove ESP32-S3 CAM Board: I picked this board because it already has a built-in camera slot and plenty of extra pins for adding parts like buttons later. Most importantly, both of its digital audio (I2S) channels are completely free to use. Unlike older boards like the ESP32-WROVER—which use up one audio channel just to run the camera—this board leaves both channels open so we can run four digital microphones and the camera at the same time. 
2. INMP441 Digital Microphones (4 pieces): I picked them because they are small and budget-friendly. Because they send pure digital sound signals directly to the main chip, we don't have to worry about static or background electrical noise messing with our audio wires.

# Circuit Diagram 

| Pin Name | Connection |
| :--- | :--- |
| VCC (all 4 mics) | 3V3 |
| GND (all 4 mics) | GND |
| L/R (Mic 1 & 3) | GND |
| L/R (Mic 2 & 4) | 3V3 |
| SD (Mic 1 & 2) | GPIO 41 |
| SD (Mic 3 & 4) | GPIO 1 |
| SCK (all 4 mics) | GPIO 39 |
| WS (all 4 mics) | GPIO 40 |

<img width="512" height="267" alt="unnamed (6)" src="https://github.com/user-attachments/assets/b8fbbefd-73ee-4d09-a468-4492c63e7df3" />

# How does it work?
Here is the basic data flow,

<img width="512" height="198" alt="unnamed (7)" src="https://github.com/user-attachments/assets/f1770118-4731-4862-80de-caa3aa84848b" />

First, the ESP32 splits the microphones into two pairs. Microphones 1 and 2 connect to the first audio channel (I2S0), and Microphones 3 and 4 connect to the second (I2S1). To keep all four microphones perfectly synchronized, I2S0 acts as the master clock and drives the timing for I2S1.

Meanwhile, the OV3660 camera is set to a low resolution (QVGA) and uses JPEG compression. Shrinking the size like this lets the ESP32 send image frames much faster (although with lower quality), keeping the FPS high for the python script.

Finally, the ESP32 packages the combined audio samples [M1, M2, M3, M4,...] and the camera frames into UDP packets. Running as a Wi-Fi Access Point (SoftAP), it streams these packets over designated ports as soon as a device connects, alternating sequentially between sending audio and image data.
