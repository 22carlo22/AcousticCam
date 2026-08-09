#ifndef CONSTANTS_H
#define CONSTANTS_H

// ==========================================
// Camera Hardware & Pin Configuration (DVP)
// ==========================================

#define PWDN_GPIO_NUM    -1       // Power Down pin (disabled / pulled down externally)
#define RESET_GPIO_NUM   -1       // Hardware Reset pin (disabled)
#define XCLK_GPIO_NUM    15       // System Master Clock driving sensor ISP
#define SIOD_GPIO_NUM     4       // SCCB I2C Data line
#define SIOC_GPIO_NUM     5       // SCCB I2C Clock line

// Parallel 8-bit Data Bus (D0 - D7)
#define Y9_GPIO_NUM      16       // Sensor Data Bit 7 (MSB)
#define Y8_GPIO_NUM      17       // Sensor Data Bit 6
#define Y7_GPIO_NUM      18       // Sensor Data Bit 5
#define Y6_GPIO_NUM      12       // Sensor Data Bit 4
#define Y5_GPIO_NUM      10       // Sensor Data Bit 3
#define Y4_GPIO_NUM       8       // Sensor Data Bit 2
#define Y3_GPIO_NUM       9       // Sensor Data Bit 1
#define Y2_GPIO_NUM      11       // Sensor Data Bit 0 (LSB)

// Video Synchronization Control Signals
#define VSYNC_GPIO_NUM    6       // Vertical Frame Sync pulse
#define HREF_GPIO_NUM     7       // Horizontal Line Reference pulse
#define PCLK_GPIO_NUM    13       // Pixel Data Clock output from camera

// ==========================================
// Dual I2S Microphone Array Pin Mapping
// ==========================================
#define AUDIO_SCK        39       // Shared Bit Clock (BCLK) driven by I2S_NUM_0 master
#define AUDIO_WS         40       // Shared Word Select / Frame Sync (LRCLK) driven by I2S_NUM_0
#define AUDIO_SD1        41       // Data line 1 for Microphones 1 & 2 (I2S_NUM_0)
#define AUDIO_SD2         1       // Data line 2 for Microphones 3 & 4 (I2S_NUM_1)

#define AUDIO_SAMPLES  1024       // Number of audio sampling points per capture block window
#define AUDIO_FREQ    44100       // PCM sampling rate (Hz)

// ==========================================
// Wi-Fi Access Point Configuration
// ==========================================
#define WIFI_NAME       "Esp32" 
#define WIFI_PASSWORD   ""        // Open AP configuration

// Network Data Streaming Ports
#define AUDIO_PORT    5010        // Outgoing UDP target port for 4-channel audio stream
#define CAM_PORT      5011        // Outgoing UDP target port for JPEG video frame stream

#endif