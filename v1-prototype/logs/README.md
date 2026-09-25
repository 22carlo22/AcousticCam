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

## August, 2026
- I added a simple user interface to tweak settings on the fly. You can set the frequency range to target specific sounds, adjust the smooth setting to stop the heatmap from flickering, tweak the blob control to sharpen the contrast, and turn on the focus feature to restrict sound detection to a small area in the middle of the camera frame.
- I ditched the slow USB serial wire for audio and stopped routing camera video through my home Wi-Fi network. Now, the ESP32 operates as its own standalone Wi-Fi hotspot (SoftAP). My laptop connects directly to it, streaming both audio and video wirelessly with almost zero lag.
- I simplified the math and cut out the unnecessary noise calibration. In addition, the script only calculates frequencies within the selected bandpass filter range instead of the whole spectrum. Ignoring those extra frequency bins saves a ton of processing power, so I can crank up the heatmap resolution without affecting the frame rate.

<img width="314" height="241" alt="633192145-bb8039ad-2e64-4c38-866b-16299a09d431" src="https://github.com/user-attachments/assets/ed97c11a-fd8e-4534-9170-7b083b882368" />
<img width="318" height="241" alt="633192147-0dcda060-4de1-4082-96f7-9b8f787db125" src="https://github.com/user-attachments/assets/ec6d0dba-7ab4-45c4-86c8-88526f2de84c" />
<img width="315" height="232" alt="633192149-01dfaaf2-2a56-4211-90cd-871e03cf4c6a" src="https://github.com/user-attachments/assets/43826d0f-e4c4-4872-9b52-db9f6d25c0fd" />

https://github.com/user-attachments/assets/a9d03c2f-2231-4bc3-bd4d-580f50ba290a
https://github.com/user-attachments/assets/e446b13b-1a56-4c70-a578-c66757d4eb09
https://github.com/user-attachments/assets/015eb1a7-138d-4f21-a774-8aaea2d0ba44
