# ESP32 Acoustic Camera

My objective is to create DIY handheld acoustic camera that is affordable.  It will compose of the following:
- ESP32 CAM Dev Board ~$25
- LCD Display Module IPS Screen 240×320  ~$20
- 4pcs INMP441 Omnidirectional Microphone Module ~$20

Want to know how the location of the sound source is calculated? read the octave folder

Want to know how the esp32 parses the 4 mics? read the firmware folder

Note: this is still work in progress. Currently, the mics are being read and syncronized by the esp32, which is sent serially to a device (ie. Octave software like Matlab) for processing the heavy calculations.

What is next? 
Translating the matlab script into C++ source code using ESP-DSP library.

# Feedback
This is an open source. Feel free to contribute and improve this project!
