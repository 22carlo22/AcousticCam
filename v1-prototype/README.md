# Description

This project is a cheap, DIY acoustic camera made with ESP32 and just 4 mics. The ESP32 streams raw audio and video over Wi-Fi to a computer running a custom Python script, which handles all the math and draws the sound heatmap. Instead of using pre-made beamforming libraries, I built the DSP code from scratch to learn how it works under the hood. Doing it this way gives me a clear blueprint to optimize the math and translate everything into C++ directly on the [ESP32 later on](../v2-standalone). 

# Updates
1. Improved sound source detection:
- I added a simple CLEAN algorithm to uncover primary sound sources masked by loud noise, coherence, or echoes
- the frequency resolution (how selectively the system differentiates acoustic pitches) can now easily be adjusted and increased to help isolate local sources
- it now accounts for curved sound waves rather than planar ones to consider nearby audio sources
- fixed a heatmap misalignment issue caused by a discrepancy between the OV3660 camera specs and the Python script's camera configuration 
2. Increased ESP32 data throughput. Audio and camera feeds now stream in parallel rather than sequentially.

# Results
## Detecting Weak, Local Sounds

In the real-world, a main sound source can easily get overwhelmed by background noise, secondary sources, or wall reflections, causing the heatmap to skew, drift, or "bleed out." The CLEAN algorithm fixes this by iteratively removing those unwanted noise sources to reveal the actual local sources underneath.

3D Printer: At first, the heatmap places the sound source near the base, but the signal bleeds into the top-left corner. Applying one iteration of CLEAN reveals the extruder cooling fan as the actual source causing that extra glare.

https://github.com/user-attachments/assets/e02eee52-d7a4-4e82-85d4-d3f464f44cb1

MP3 Player near a wall: Placing the speaker near a wall causes a skewed heatmap due to strong echo reflections. CLEAN separates the speaker's direct audio from the wall reflection.

https://github.com/user-attachments/assets/07fbba67-d2ec-492c-bee9-5a7ba3348199

Electric Toothbrush: Without CLEAN, sound appears spread across the entire toothbrush. With CLEAN enabled, two distinct points stand out: the vibrating brush head and the motor housing inside the handle.

https://github.com/user-attachments/assets/37e37853-5b03-45f8-b363-d626f990d747

Tip: The CLEAN algorithm works best on a stable heatmap. Try turning up the smoothing filter (slide Smooth to the left) before cranking up the Clean slider to keep the heatmap from jumping around.

## Focusing on Specific Sounds
Every sound source has its own characteristic frequency profile, so the most effective approach is to manually apply a dynamic bandpass filter to block out unwanted frequencies. In this example, an earbud and an MP3 player are both playing white noise, but at different pitch ranges. By adjusting the Frequency Range and toggling Enable Focus, you can easily isolate each sound source on the heatmap. 

https://github.com/user-attachments/assets/d0f98324-4918-4442-a4ba-4d976ba0ad37

## Sharpening the Heatmap
With only 4 microphones, lower frequencies typically create large, blurry heatmaps. The Blob setting trims away this excess blur, producing a much sharper hotspot directly over the sound source. In the following electric shaver example, notice how sharpening the heatmap uncovers two faint local sources.

https://github.com/user-attachments/assets/e6ea4e0d-0dd2-42fd-9440-de2cb8b09dd3

## Detecting Moving Sound Sources 
The following examples demonstrate how the system tracks moving sound sources. For fast-moving targets, it is recommended to lower the smoothing filter, ensuring the heatmap updates immediately with the most recent audio data.

Roomba Vacuum:

https://github.com/user-attachments/assets/947581d9-420b-485a-a911-e0c2b0ab0f9f

Scraping a Palette Knife on Canvas:

https://github.com/user-attachments/assets/7409bcad-c6fa-48bc-b7a7-bbed28ceb19e

## Reducing Noise 
Room echoes and background noise can cause the heatmap to jump around. Applying a smoothing filter cleans up that flicker, keeping the display steady on continuous sounds. This example is demonstrated by tapping a table.

https://github.com/user-attachments/assets/ad6a0cf0-6f90-4a66-b31c-322f44a305bd


# Common Questions

### Is the frequency range limited to the hardware?
Yes, but hardware is only part of the limit. The microphone used in this project (INMP441) has a theoretical frequency range of 60 Hz to 15,000 Hz, but the real bottleneck is the physical distance between the microphones (the microphone array size). 

The script automatically applies a bandpass filter based on the array's dimensions. Without this filter, high frequencies can cause spatial aliasing (false peaks and ripples on the heatmap), while low frequencies can cause the heatmap to become overly blurry.

### Is there a way to detect lower or higher frequencies?
Yes. Changing the physical size of the microphone array directly shifts its effective frequency range: reducing the array size allows you to detect higher frequencies, while expanding it enables the detection of lower frequencies. 

### Can I add more microphones?
No. The ESP32 used in this project only has two I2S peripherals, which limits synchronous sampling to a maximum of 4 microphones (2 per I2S channel in stereo). Adding more microphones would require migrating to a microcontroller with more I2S interfaces or using an FPGA to handle parallel array sampling.

### Why do you only use phase to locate sound? Can you also use volume (amplitude) as well?
Using sound volume is tricky and usually doesn't work well with cheap microphones. The microphones I use don't all have the same sensitivity. Some are naturally louder than others. This causes the heatmap to get pulled toward the louder microphone.

You could try to calibrate them by placing a sound source directly in the middle, but room echoes instantly mess up those measurements. Unless you are in a completely echo-proof room, volume is just too unreliable to use for locating sound.

### If echoes cause inaccuracies, can't you detect and remove late sound arrivals (echoes) like LiDAR does?
That approach works for short, transient noises, like a quick beep or a clap, where you can clearly separate the initial sound from its echo. However, most everyday sound sources are continuous (like motors or fans). Once a continuous sound starts, the direct sound and its echoes overlap constantly, making it impossible to isolate the echo's arrival time.

## Quick Navigation
- [ESP32-to-Python Communication](code-esp32-firmware/README.md#how-does-it-work)
- [Microphone Array Diagram](code-esp32-firmware/README.md#circuit-diagram)
- [Math Stuff Used for Beamforming](code-python-script/README.md#how-does-it-work)
- [How to Use the Python Script](code-python-script/README.md#how-to-use)
- [How to Increase Heatmap Resolution](code-python-script/README.md#about-configpy)
- [Previous Prototypes](logs/README.md)







