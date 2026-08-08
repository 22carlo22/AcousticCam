# Description

This project is a cheap, DIY acoustic camera made with an ESP32 and just 4 mics to see if a simple setup can actually pinpoint sound on a camera feed. The ESP32 streams raw audio and video over Wi-Fi to a computer running a custom Python script, which handles all the math and draws the sound heatmap. Instead of using pre-made beamforming libraries, I built the DSP code from scratch to learn how it works under the hood. Doing it this way gives me a clear blueprint to optimize the math and translate everything into C++ directly on the [ESP32 later on](../v2-standalone). 
