#ifndef I2S_AUDIO_H
#define I2S_AUDIO_H

#include "driver/i2s.h" 
#include "Constants.h"

/**
 * @brief Manages dual-peripheral (I2S0 & I2S1) synchronized hardware audio capture 
 * for a 4-channel microphone array.
 *
 * Utilizes hardware clock synchronization over internal ESP32 GPIO matrix routes to 
 * sample 4 phase-locked audio channels simultaneously across two dual-channel 
 * microphone buses.
 */
class I2SAudio {
private:
    /** Raw DMA transfer buffer for I2S0 peripheral holding stereo audio (Channels 1 & 2). */
    int32_t buf0[2 * AUDIO_SAMPLES];

    /** Raw DMA transfer buffer for I2S1 peripheral holding stereo audio (Channels 3 & 4). */
    int32_t buf1[2 * AUDIO_SAMPLES];
    
public:
    /** 
     * Memory storage holding demuxed and interleaved 4-channel 32-bit PCM audio samples.
     * Array layout: [Mic1_0, Mic2_0, Mic3_0, Mic4_0, Mic1_1, Mic2_1, ...]
     */
    int32_t buf[4 * AUDIO_SAMPLES];

    /**
     * @brief Configures I2S0 (Master) and I2S1 (Slave), maps GPIO matrix interconnections, 
     * resets peripheral clocks, and starts synchronized hardware DMA sampling.
     */
    void init();

    /**
     * @brief Reads DMA buffers from both I2S hardware peripherals, bit-shifts 
     * 24-bit left-aligned samples to 32-bit signed PCM integers, and interleaves all 4 channels.
     */
    void sample();
};

#endif // I2S_AUDIO_H