#include <Arduino.h>
#include "Constants.h"
#include "Cam.h"
#include "I2SAudio.h"
#include "SoftAp.h"

// Global Hardware Object Instantiations
I2SAudio audio = I2SAudio();
int32_t buf[4 * AUDIO_SAMPLES]; // Memory storage for interleaved 4-channel audio samples

Cam camera;
SoftAp ap = SoftAp(WIFI_NAME, WIFI_PASSWORD);

void setup() {
    Serial.begin(115200);

    // Initialize all hardware peripherals and networking tasks
    audio.init();
    camera.init();
    ap.begin();
    
    // Bind streaming UDP sockets
    ap.startPort(AUDIO_PORT);
    ap.startPort(CAM_PORT); 
}

void loop() {
    static uint8_t counter = 0; // Frame sequence tracking ID for UDP chunk reassembly

    // 1. Capture 4-channel audio block and transmit over UDP
    audio.sample(buf);
    ap.send(AUDIO_PORT, counter, (uint8_t*) buf, 4 * AUDIO_SAMPLES * sizeof(int32_t));

    // 2. Request JPEG video frame from camera ISP and transmit over UDP
    camera_fb_t *fb = camera.readRequest();
    if (fb != NULL) {
        ap.send(CAM_PORT, counter, fb->buf, fb->len);
        camera.readComplete(fb); // Free PSRAM frame buffer back to driver pool
    }

    // Increment frame sequence ID (wraps automatically at 255)
    counter++;
}