# Description 
An acoustic camera is an awesome tool. It lets you actually see sound layered over a live camera view! However, buying one can cost thousands of dollars. If you want to learn how they work and build your own using cheap, off-the-shelf parts, this project is maybe for you.

Project Modules
1. [V1 Prototype](v1-prototype/) (Python Hybrid): My working setup. The ESP32 handles the camera feed and 4-microphone array, while a host Python script performs the heavy audio processing and heatmap rendering.
2. [V2 Standalone](v1-standalone/) (In Progress): The ultimate goal. A fully portable, self-contained acoustic camera where the ESP32 handles both audio acquisition and DSP calculations directly on the chip. 
