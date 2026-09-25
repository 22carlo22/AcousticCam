#include "Cam.h"
#include "Constants.h"
#include <Arduino.h>

void Cam::init() {
    camera_config_t config;
    
    // Assign PWM timer channel to generate XCLK master clock for camera ISP
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    
    // Map parallel 8-bit DVP data bus pins
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    
    // Map timing control and SCCB register configuration pins
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    
    // Clock & Resolution Configuration
    config.xclk_freq_hz = 20000000;       // Output 20 MHz master clock to OV2640 sensor
    config.frame_size = FRAMESIZE_QVGA;   // Capture resolution: 320 x 240 pixels

    // Buffer & Compression Settings
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM; // Store frame buffers in external PSRAM
    config.jpeg_quality = 10;                // Quality range 1-63 (lower = higher image fidelity)
    config.fb_count = 2;                     // Double-buffered queue to prevent frame tearing/drops

    // Initialize ESP camera hardware driver
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[ERROR] Camera driver initialization failed with error: 0x%x\n", err);
    }
}

camera_fb_t* Cam::readRequest() {
    // Non-blocking fetch of next frame buffer from camera driver DMA ring buffer
    return esp_camera_fb_get();
}

void Cam::readComplete(camera_fb_t* fb) {
    // Return frame buffer descriptor back to DMA pool for reuse
    esp_camera_fb_return(fb);
}