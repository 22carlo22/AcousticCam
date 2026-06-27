# ESP32 Acoustic Camera
Acoustic cameras are incredibly cool devices—they literally let you see sound in real-time. However, professional ones cost thousands of dollars. The goal of this project is to figure out the secrets behind how they work and build a simple version using parts anyone can buy:
- Freenove ESP32-S3 CAM Board
- IPS LCD Display Screen (240×320) 
- 4x INMP441 Digital Microphones 

# Updates
- Switched from GNU Octave to Python: I started out writing the math scripts in Octave (an open-source MATLAB alternative). But Octave gave me huge headaches when trying to do camera streams due to compatibility issues. Moving the math over to a multi-threaded Python script fixed everything and made it much faster.
- Upgraded the Main Brain (ESP32-WROVER to ESP32-S3): During early testing, I discovered a major hardware conflict—the older WROVER board shares its internal camera clock lines with one of its I2S peripheral buses. Activating the camera physically disabled two of my microphones. Upgrading to the ESP32-S3 gave me two completely independent I2S buses, allowing all 4 microphones to sample simultaneously alongside the camera.
- Cleaner Frame & Thinner Wires: I redesigned the physical body of the prototype to be symmetrical and replaced thick jumper wires with thin ones. The previous prototype were actually bouncing sound waves around, creating mini "echoes" that threw off the phase calculations.
- It Works! The code is now highly optimized, and you can officially see sound mapped directly on top of the live video stream.

# Results
Here is what the current prototype looks like, along with a real test tracking a trimmer. The bright red spot shows the loudest sound.

<img width="4624" height="3472" alt="PXL_20260627_054831126" src="https://github.com/user-attachments/assets/a1fb31c7-43e8-4827-aea0-15ae16da2077" />

https://github.com/user-attachments/assets/54ef5966-bea8-424f-9d58-3ecbc37549db

# Technical Stuff:
- [Firmware](./acoustic-firmware/README.md) – Read this to see how the ESP32 works.
- [The Math Behind the Camera](./acoustic-scripts/README.md) – Read this to see the simple formulas used to track sound waves in space, and techniques to reduce "ghost" sounds.

# Next of Agenda: 
Right now, the ESP32 just collects the data, and my laptop does all the heavy math calculations in Python. My next big goal is to move all of that math processing directly onto the tiny ESP32 chip itself.


