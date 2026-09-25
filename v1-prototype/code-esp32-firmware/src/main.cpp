#include <Arduino.h>
#include "Constants.h"
#include "Cam.h"
#include "I2SAudio.h"
#include "SoftAp.h"

// Instantiate hardware peripheral and network interface objects globally
I2SAudio audio;
Cam camera;
SoftAp ap = SoftAp(WIFI_NAME, WIFI_PASSWORD, IP);

// --- Task 1: Dedicated Audio Task (Core 0) ---
void audioTask(void *pvParameters) {
    while (true) {
        // 1. Block execution until audio.buf is completely populated by DMA hardware transfer
        audio.sample();

        // 2. Transmit demuxed 4-channel audio frame over dedicated TCP port
        ap.send(AUDIO_PORT, (uint8_t*)audio.buf, sizeof(audio.buf));
    }
}

// --- Task 2: Dedicated Camera Task (Core 1) ---
void cameraTask(void *pvParameters) {
    while (true) {
        // 1. Fetch JPEG frame buffer pointer from camera driver DMA ring buffer
        camera_fb_t *fb = camera.readRequest();
        if (fb != NULL) {
            // 2. Transmit raw JPEG payload block over dedicated video TCP port
            ap.send(CAM_PORT, fb->buf, fb->len);

            // 3. Release frame buffer memory block back to the camera DMA pool
            camera.readComplete(fb);
        }


        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

void setup() {
    Serial.begin(115200);

    // Initialize hardware drivers and Wi-Fi Access Point interface
    audio.init();
    camera.init();
    ap.begin();
    
    // Open dynamic TCP server ports for incoming stream clients
    ap.startPort(AUDIO_PORT);
    ap.startPort(CAM_PORT); 

    // Create Audio Processing Task pinned to Core 0 (Isolates audio pipeline)
    xTaskCreatePinnedToCore(
        audioTask,    
        "AudioTask",   
        8192,          
        NULL,          
        1,             
        NULL,          
        0             
    );

    // Create Camera Processing Task pinned to Core 1 (Isolates video processing)
    xTaskCreatePinnedToCore(
        cameraTask,    
        "CameraTask",  
        8192,          
        NULL,          
        1,             
        NULL,          
        1              
    );
}

void loop() {
    vTaskDelete(NULL); 
}