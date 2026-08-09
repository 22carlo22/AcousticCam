#ifndef I2S_AUDIO_H
#define I2S_AUDIO_H

#include "driver/i2s.h" 

/**
 * @brief Class managing dual-peripherals (I2S0 & I2S1) synchronized hardware audio capture 
 * for a 4-channel microphone array.
 */
class I2SAudio {
public:
    /**
     * @brief Configures I2S0 (Master) and I2S1 (Slave), maps GPIO matrix interconnections, 
     * resets peripheral clocks, and starts synchronized hardware DMA sampling.
     */
    void init();

    /**
     * @brief Performs a blocking DMA read from both I2S peripherals, demuxes and scales 
     * the 32-bit audio samples into an interleaved 4-channel contiguous PCM array.
     * @param buf Pointer to target output array of size (4 * AUDIO_SAMPLES).
     */
    void sample(int32_t *buf);
};

#endif