#ifndef CONSTANTS_H
#define CONSTANTS_H

// Camera
#define JPEG_FORMAT

#define CAM_WIDTH 320
#define CAM_HEIGHT 240

#define PWDN_GPIO_NUM    -1
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    15
#define SIOD_GPIO_NUM     4
#define SIOC_GPIO_NUM     5

#define Y9_GPIO_NUM      16
#define Y8_GPIO_NUM      17
#define Y7_GPIO_NUM      18
#define Y6_GPIO_NUM      12
#define Y5_GPIO_NUM      10
#define Y4_GPIO_NUM       8
#define Y3_GPIO_NUM       9
#define Y2_GPIO_NUM      11

#define VSYNC_GPIO_NUM    6
#define HREF_GPIO_NUM     7
#define PCLK_GPIO_NUM    13

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
#define AUDIO_SCK 39
#define AUDIO_WS  40
#define AUDIO_SD1 41
#define AUDIO_SD2 1

#define AUDIO_SAMPLES 1024
#define AUDIO_FREQ 44100
#define REQ_AUDIO_DATA 0

// Wifi
#define WIFI_ID         "AshEstates"
#define WIFI_PASSWORD   "butfirstwifi"

// Video stream
#define UDP_IP          "192.168.1.74"
#define UDP_SOCKET      5005

#endif