#ifndef I2S_AUDIO_H
#define I2S_AUDIO_H

#include "driver/i2s.h" 

class I2SAudio {
public:
    void init();
    void sample(int32_t *buf);
};

#endif