# ESP32 Acoustic Camera

My objective is to create simple acoustic camera using esp32, that is affordable and manageable to build by a hobbyist.  It will compose of the following:
- $25 ESP32 CAM Dev Board 
- $20 LCD Display Module IPS Screen 240×320 
- $20 4pcs INMP441 Omnidirectional Microphone Module

Note: this is still a work in progress. The ESP32 currently reads and synchronizes the mic data before sending it serially to a host device for the calculations. Here is the prototype, 

![PXL_20260406_221517308](https://github.com/user-attachments/assets/636ea669-2af8-4f88-829e-7a58ab6031be)

# Test Result

In this test, I use an ear bud to produce a 2KHz.

![GIF_20260407_001901_685](https://github.com/user-attachments/assets/2f5d6e8a-2f1b-4da5-b624-e3df61f7b9f6)

April 20: The script can now pinpoint the location of various frequency; it can now locate more than one sound source! 

<img width="492" height="277" alt="GIF_20260420_210139_500" src="https://github.com/user-attachments/assets/f1701a3e-be62-45ef-97c3-9c5914c32b69" />

# Feedback
This is an open source. Feel free to contribute and improve this project!
