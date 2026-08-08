# Project Logs
This folder contains early prototypes, and test results that laid the foundation for the entire project.

## Early April, 2026
My first goal was simply to play around with the basic math equations and see if it was actually possible to pinpoint a sound using only 4 microphones. Spoiler alert: it is! For this test, I used a standard earbud to play a steady, single-frequency tone. I dumped the raw matrix data and used GNU Octave to run the calculations.

<img width="2298" height="3037" alt="574454858-636ea669-2af8-4f88-829e-7a58ab6031be" src="https://github.com/user-attachments/assets/c49da3e1-af8d-465c-857f-6a72a016984e" />

<img width="656" height="368" alt="574456689-2f5d6e8a-2f1b-4da5-b624-e3df61f7b9f6" src="https://github.com/user-attachments/assets/9e0efba2-9d2d-4522-955b-50b06bb6b868" />

## April 20, 2026
Once the basic math was proven, my next goal was to split the sound processing so the camera could calculate locations for individual frequencies. This upgrade allows the system to track multiple different kinds of real-world noises at the same time instead of just a single steady tone. I used GNU Octave to build and verify this.

<img width="492" height="277" alt="581115861-f1701a3e-be62-45ef-97c3-9c5914c32b69" src="https://github.com/user-attachments/assets/819d71fa-0784-4388-abc8-cb8feac08d7a" />

## Early July , 2026
- Switched from GNU Octave to Python: I started out writing the math scripts in Octave (an open-source MATLAB alternative). But Octave gave me huge headaches when trying to do camera streams due to compatibility issues. Moving the math over to a multi-threaded Python script fixed everything and made it much faster.
- Upgraded the Main Brain (ESP32-WROVER to ESP32-S3): During early testing, I discovered a major hardware conflict—the older WROVER board shares its internal camera clock lines with one of its I2S peripheral buses. Activating the camera physically disabled two of my microphones. Upgrading to the ESP32-S3 gave me two completely independent I2S buses, allowing all 4 microphones to sample simultaneously alongside the camera.
- Cleaner Frame & Thinner Wires: I redesigned the physical body of the prototype to be symmetrical and replaced thick jumper wires with thin ones. The previous prototype were actually bouncing sound waves around, creating mini "echoes" that threw off the phase calculations.

https://github.com/user-attachments/assets/3a1db111-f592-4701-8f68-1e2bb4d3ebd6


