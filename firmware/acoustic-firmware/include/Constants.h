#ifndef CONSTANTS_H
#define CONSTANTS_H

// Camera
#define CAM_WIDTH 320
#define CAM_HEIGHT 240

#define PWDN_GPIO_NUM -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 21
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 19
#define Y4_GPIO_NUM 18
#define Y3_GPIO_NUM 5
#define Y2_GPIO_NUM 4
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

// Screen
#define STRIP_HEIGHT 20
#define ORIENTATION 1

// HotSpot
#define SEARCH_GRID_WIDTH 64
#define SEARCH_GRID_HEIGHT 48
#define NOISE_RANGE_SCALE 8            // Captures sound: NOISE_BASE <= sound_intensity < (NOISE_BASE + 2^NOISE_RANGE_SCALE) 
#define NOISE_BASE 50
#define ALPHA 127                       //Must be: 0 <= ALPHA <= 256

// Microphone (I2S)
#define AUDIO_SCK1 0
#define AUDIO_WS1  2
#define AUDIO_SD1 15
#define AUDIO_SCK2 32
#define AUDIO_WS2  33
#define AUDIO_SD2 13
#define AUDIO_SAMPLES 1024
#define AUDIO_FREQ 44100


// Priority keyword
#define LOW_PRIORITY 0
#define HIGH_PRIORITY 2


#define foo(val) Serial.println(val)

#endif