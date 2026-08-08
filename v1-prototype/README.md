# Description

This project is a cheap, DIY acoustic camera made with ESP32 and just 4 mics to see if a simple setup can actually pinpoint sound on a camera feed. The ESP32 streams raw audio and video over Wi-Fi to a computer running a custom Python script, which handles all the math and draws the sound heatmap. Instead of using pre-made beamforming libraries, I built the DSP code from scratch to learn how it works under the hood. Doing it this way gives me a clear blueprint to optimize the math and translate everything into C++ directly on the [ESP32 later on](../v2-standalone). 

# Updates
1. I added a simple user interface to tweak settings on the fly. You can set the frequency range to target specific sounds, adjust the smooth setting to stop the heatmap from flickering, tweak the blob control to sharpen the contrast, and turn on the focus feature to restrict sound detection to a small area in the middle of the camera frame.
2. I ditched the slow USB serial wire for audio and stopped routing camera video through my home Wi-Fi network. Now, the ESP32 operates as its own standalone Wi-Fi hotspot (SoftAP). My laptop connects directly to it, streaming both audio and video wirelessly with almost zero lag.
3. I simplified the math and cut out the unnecessary noise calibration. In addition, the script only calculates frequencies within the selected bandpass filter range instead of the whole spectrum. Ignoring those extra frequency bins saves a ton of processing power, so I can crank up the heatmap resolution without affecting the frame rate.

# Results

## Separating two sound sources
In this test, an earbud and an MP3 player both play white noise, but at different pitches. By adjusting the Frequency Range and turning on Enable Focus, you can easily isolate each sound source on its own.

https://github.com/user-attachments/assets/da40b979-48a1-4a11-9fc6-00c4d3ec7ee4

## Sharpening the Heatmap
With only 4 microphones, lower frequencies normally create big, blurry clouds on the screen. I added a Blob setting that trims away that extra blur, giving you a much sharper spot right over the sound source (tested here with a solder exhaust fan).

https://github.com/user-attachments/assets/184bc9f9-1429-49bd-8658-c018d527062a

## Reducing Echoes & Flickering
Room echoes and background noise can make the heatmap jump around quickly. Adding a Smooth feature cleans up that flicker, keeping the heatmap steady on constant, continuous sounds. In this test, I demonstrated it by scratching the back of a phone. 

https://github.com/user-attachments/assets/a27e0d70-72e1-46ec-ab69-e4719303e28d

## Extra Scans
Here are a few more acoustic snapshots taken of different objects,

<img width="315" height="232" alt="Screenshot 2026-07-30 163546" src="https://github.com/user-attachments/assets/01dfaaf2-2a56-4211-90cd-871e03cf4c6a" />

<img width="318" height="241" alt="Screenshot 2026-07-30 161036" src="https://github.com/user-attachments/assets/0dcda060-4de1-4082-96f7-9b8f787db125" />

<img width="314" height="241" alt="Screenshot 2026-07-30 162210" src="https://github.com/user-attachments/assets/bb8039ad-2e64-4c38-866b-16299a09d431" />

## Quick Navigation
- [ESP32-to-Python Communication](code-esp-firmware/README.md)







