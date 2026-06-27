# Description 
Right now, the code flashed onto the ESP32 chip has two simple jobs:
1. It reads and synchronizes the sound coming from all 4 microphones at the exact same time.
2. It turns on the attached camera and streams the video out wirelessly.

# Parts 
-Freenove ESP32-S3 Cam Board: This is the main "brain" of the project. I chose this specific chip because it has a built-in slot for a camera, and it has plenty of extra pin connectors. This means I can easily expand the project later by plugging in hardware like a control buttons. Most importantly, it has two independent sound accelerators inside it, which is exactly what lets us run up to 4 digital microphones at once.
-INMP441 Digital Microphones (4 pieces): These are the ears of the project. I picked them because they are small and budget-friendly (I bought a 4-pack on Amazon for around $20 CAD). Because they send pure digital sound signals directly to the main chip, we don't have to worry about static or background electrical noise messing with our audio wires.

<img width="2298" height="3037" alt="574454858-636ea669-2af8-4f88-829e-7a58ab6031be" src="https://github.com/user-attachments/assets/acc8a7a5-de29-495e-8e95-80a89d772424" />

# How does it work? 
To locate exactly where a sound is coming from, all four microphones must be perfectly synchronized down to the microsecond. The ESP32 handles this by splitting the microphones into pairs: Microphones 1 and 2 plug into the first audio peripheral (I2S0), while Microphones 3 and 4 connect to the second one (I2S1). To ensure every microphone takes a snapshot of the sound at the exact same instant, the system uses a master-slave clock configuration. By setting I2S0 as the master clock and forcing I2S1 to act as its slave, the second audio bus mirrors the first one's timing pulses perfectly.

The collected audio data is kept entirely off the wireless network to prevent bottlenecks. Instead of using Wi-Fi, the system relies on a physical USB serial cable. The host Python script sends a quick "request" byte down the wire, and the ESP32 instantly responds by sending back a neat line of interleaved audio samples formatted as [Mic1, Mic2, Mic3, Mic4, Mic1, Mic2, Mic3, Mic4...].

Meanwhile, the video stream operates completely independently in the background. The moment the ESP32 powers on, the camera automatically captures frames, compresses them into JPEG images, and blasts them over Wi-Fi using a UDP protocol.

By offloading the high-bandwidth audio data to a physical USB serial connection, the Wi-Fi radio is freed up entirely for video streaming. This dual-pathway design maximizes data throughput to the Python script, resulting in a much higher frame rate (FPS).

<img width="581" height="291" alt="Acoustic-flow-diagram drawio" src="https://github.com/user-attachments/assets/157e8f0b-5ef8-41e6-9bd7-f0a2c943a017" />
