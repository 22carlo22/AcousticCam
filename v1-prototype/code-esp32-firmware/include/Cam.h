#ifndef CAM_H
#define CAM_H

#include <stdint.h>
#include "esp_camera.h"

/**
 * @brief Manages OV2640 camera hardware initialization, pin routing, and frame buffer capture.
 *
 * Configures the ESP32 camera driver with DVP parallel interface pins, generates the 20MHz XCLK,
 * and manages double-buffered JPEG image frame acquisition in PSRAM.
 */
class Cam {
public:
    /**
     * @brief Sets up camera hardware pins, LEDC clock output, JPEG ISP parameters, and PSRAM frame buffers.
     */
    void init();

    /**
     * @brief Fetches an active JPEG image frame buffer from the camera driver DMA queue.
     * 
     * @return camera_fb_t* Pointer to the captured camera frame buffer struct, or NULL on capture failure.
     */
    camera_fb_t* readRequest();

    /**
     * @brief Releases a processed frame buffer back to the camera driver DMA queue pool.
     * 
     * @param fb Pointer to the camera frame buffer struct to return.
     */
    void readComplete(camera_fb_t* fb);
};

#endif // CAM_H