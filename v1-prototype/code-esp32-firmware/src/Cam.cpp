#include "Cam.h"
#include "Constants.h"
#include <Arduino.h>

/**
 * @brief Sets up hardware pins, LEDC clock output, JPEG ISP options, and PSRAM frame buffers.
 */
void Cam::init() {
    camera_config_t config;
    
    // Assign PWM timer channel to generate XCLK master clock for camera ISP
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    
    // Map parallel 8-bit DVP data pins
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    
    // Map timing and SCCB configuration pins
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    
    config.xclk_freq_hz = 20000000;       // Output 20 MHz master clock to OV2640
    config.frame_size = FRAMESIZE_QVGA;   // Resolution: 320 x 240

    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM; // Store image buffers in external PSRAM
    config.jpeg_quality = 10;                 // Scale 1-63 (lower = higher image fidelity)
    config.fb_count = 2;                      // Double-buffered capture queue to prevent frame drops

    // Initialize ESP camera driver hardware
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[ERROR] Camera driver initialization failed with error: 0x%x\n", err);
    }
}

/**
 * @brief Fetches a frame buffer from driver queue.
 */
camera_fb_t* Cam::readRequest() {
    return esp_camera_fb_get();
}

/**
 * @brief Releases frame buffer back to DMA pipeline pool.
 */
void Cam::readComplete(camera_fb_t* fb) {
    esp_camera_fb_return(fb);
}