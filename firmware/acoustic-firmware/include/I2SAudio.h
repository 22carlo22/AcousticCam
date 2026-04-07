#ifndef I2SAUDIO_H
#define I2SAUDIO_H

#include <Arduino.h>
#include <driver/i2s.h>

class I2SAudio{
    public:
        void init();
        void sample(int32_t *buf);

};

#endif