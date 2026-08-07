# Description 
This section is still a work in progress. Unlike Version 1, which relies on a Python script to handle heavy calculations, the main goal of Version 2 is to do all processing directly on the ESP32. This will make it a fully portable, standalone acoustic camera!
Below is the planned hardware list and project design.

# Parts 

1. Freenove ESP32-S3 CAM Board: Includes a built-in camera interface and 2 available hardware I2S peripherals. Also, it is equipped with SIMD! <img width="276" height="456" alt="unnamed" src="https://github.com/user-attachments/assets/013bf5b2-034d-4069-9390-df3399246dda" />
2. 4x INMP441: supports I2S protocol. <img width="193" height="155" alt="unnamed (1)" src="https://github.com/user-attachments/assets/58bdedbd-dcb6-480f-b1e1-395d43c584f2" />
3. Waveshare 2inch LCD Display: supports SPI communication. <img width="272" height="225" alt="unnamed (2)" src="https://github.com/user-attachments/assets/5e713609-568c-4c80-adcf-87ff1bd98039" />
4. Rotary Encoder: Provides physical user controls. <img width="285" height="293" alt="unnamed (3)" src="https://github.com/user-attachments/assets/4c0de1c2-b756-465b-8eb9-bfecf3c7e451" />

# Plan 

  My plan uses the ESP32’s dual cores and hardware features to split up tasks so everything runs smoothly at the same time (shown in the diagram below) . The microphones collect audio in the background using I2S, while the camera captures live video frames directly in color RGB format. Core 0 handles all the heavy audio math, calculating where the sound is coming from as soon as new sound data arrives. Meanwhile, Core 1 takes those calculated sound locations and draws a heat map directly on top of the live camera picture. Once that combined frame is ready, the SPI DMA streams the image straight to the screen.

<img width="512" height="261" alt="unnamed (4)" src="https://github.com/user-attachments/assets/dc962c58-2fd9-42b3-bcec-39867622770f" />

  To keep this loop running continuously, I will use double buffers using FreeRTOS queues. The timing for each stage breaks down logically: collecting 1024 audio samples at 44.1 kHz takes about 23 ms, capturing a full QVGA RGB picture takes roughly 50 ms, and pushing that finished frame to the TFT screen over SPI takes about 30 ms.
Because the camera frame capture is our biggest bottleneck at 50 ms, my main target is to keep both the audio math on Core 0 and the heatmap rendering on Core 1 under 50 ms each. As long as the processing steps complete within that window, the entire system will run at a steady 20 fps.

  To ensure the calculations run as fast as possible, I will use the esp-dsp library, which relies on custom assembly instructions to take advantage of the ESP32-S3's hardware SIMD vector processing. If floating-point math still turns out to be too slow, my backup plan is to convert the calculations to fixed-point integer math to double the processing speed.



