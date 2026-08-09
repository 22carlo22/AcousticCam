#include "I2SAudio.h"
#include "Constants.h"
#include "driver/gpio.h"
#include "soc/system_reg.h"    
#include <Arduino.h>  

/**
 * @brief Configures I2S0 (Master) and I2S1 (Slave) peripherals for phase-locked 
 * 4-channel audio sampling from two dual-channel I2S microphones.
 */
void I2SAudio::init() {
    // 1. Define I2S Master Configuration (I2S_NUM_0)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = AUDIO_FREQ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, 
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo capture per I2S data line
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = AUDIO_SAMPLES,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // Install driver for I2S_NUM_0 (Master Clock Generator)
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);

    // Bind physical pin routing for I2S Master
    i2s_pin_config_t pins0 = {
        .bck_io_num = AUDIO_SCK,        // Master Bit Clock output pin
        .ws_io_num = AUDIO_WS,          // Master Word Select (LRCLK) output pin
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD1        // Data input line 1 (Channels 1 & 2)
    };
    i2s_set_pin(I2S_NUM_0, &pins0);

    // 2. Define I2S Slave Configuration (I2S_NUM_1)
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_SLAVE | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);

    // Bind data pin for I2S Slave (Clock pins driven externally via GPIO matrix interconnections)
    i2s_pin_config_t pins1 = {
        .bck_io_num = I2S_PIN_NO_CHANGE, 
        .ws_io_num = I2S_PIN_NO_CHANGE,  
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD2         // Data input line 2 (Channels 3 & 4)
    };
    i2s_set_pin(I2S_NUM_1, &pins1);

    // 3. Connect Master Clock Signals into I2S1 Slave Peripheral via GPIO Matrix
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_SCK]);
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_WS]);
    gpio_matrix_in((uint32_t)AUDIO_SCK, (uint32_t)I2S1I_BCK_IN_IDX, false);
    gpio_matrix_in((uint32_t)AUDIO_WS,  (uint32_t)I2S1I_WS_IN_IDX,  false);

    // 4. Synchronously Reset both I2S Hardware State Machines
    i2s_stop(I2S_NUM_0);
    i2s_stop(I2S_NUM_1);

    // Toggle hardware peripheral reset flags in system control registers
    REG_SET_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);
    REG_CLR_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);

    // Start slave interface first so it is primed to latch the moment the master clock starts
    i2s_start(I2S_NUM_1); 
    i2s_start(I2S_NUM_0);    
}

/**
 * @brief Reads DMA buffers from both I2S channels, converts 24-bit aligned sampling data 
 * to standard 32-bit integers, and interleaves them.
 */
void I2SAudio::sample(int32_t *buf) {
    static int32_t buf0[2 * AUDIO_SAMPLES], buf1[2 * AUDIO_SAMPLES];
    size_t bytes_read0, bytes_read1;
    
    // Blocking read from both DMA buffers until complete sample frame arrives
    i2s_read(I2S_NUM_0, buf0, 2 * AUDIO_SAMPLES * sizeof(int32_t), &bytes_read0, portMAX_DELAY);
    i2s_read(I2S_NUM_1, buf1, 2 * AUDIO_SAMPLES * sizeof(int32_t), &bytes_read1, portMAX_DELAY);
    
    // Demux and bit-shift 24-bit left-justified raw audio into signed 32-bit PCM values:
    // Format: buf[n] = [Mic1, Mic2, Mic3, Mic4, Mic1, Mic2, ...]
    for (int i = 0; i < AUDIO_SAMPLES; i++) {
        buf[i * 4]     = buf0[i * 2] >> 8;      // Mic 1 (I2S0 Left Channel)
        buf[i * 4 + 1] = buf0[i * 2 + 1] >> 8;  // Mic 2 (I2S0 Right Channel)
        buf[i * 4 + 2] = buf1[i * 2] >> 8;      // Mic 3 (I2S1 Left Channel)
        buf[i * 4 + 3] = buf1[i * 2 + 1] >> 8;  // Mic 4 (I2S1 Right Channel)
    }
}