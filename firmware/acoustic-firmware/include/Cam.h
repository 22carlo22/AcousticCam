#ifndef CAM_H
#define CAM_H

#include <stdint.h>
#include "esp_camera.h"

class Cam{
    public:
        void init();
        camera_fb_t* readRequest();
        void readComplete(camera_fb_t* fb);
};

#endif