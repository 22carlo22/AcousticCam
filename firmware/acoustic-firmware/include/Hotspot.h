#ifndef HOTPSPOT_H
#define HOTSPOT_H

#include <Arduino.h>


class Hotspot{
    private:
        uint8_t rgb_map[256*3];

    public:
        void init();
        void apply(uint16_t *img, int32_t *sound);
};


#endif