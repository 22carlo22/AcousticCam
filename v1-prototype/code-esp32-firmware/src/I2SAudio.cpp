#include "I2SAudio.h"
#include "Constants.h"
#include "driver/gpio.h"
#include "soc/system_reg.h"    
#include <Arduino.h>  

void I2SAudio::init() {
    // Define master I2S0 peripheral configuration
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = AUDIO_FREQ_HZ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, 
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 10,
        .dma_buf_len = AUDIO_SAMPLES,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // Install driver and configure physical GPIO pins for master (I2S0)
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);

    i2s_pin_config_t pins0 = {
        .bck_io_num = AUDIO_SCK,        
        .ws_io_num = AUDIO_WS,          
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD1        
    };
    i2s_set_pin(I2S_NUM_0, &pins0);

    // Reconfigure settings for slave mode and install driver on I2S1
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_SLAVE | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);

    i2s_pin_config_t pins1 = {
        .bck_io_num = I2S_PIN_NO_CHANGE, 
        .ws_io_num = I2S_PIN_NO_CHANGE,  
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD2         
    };
    i2s_set_pin(I2S_NUM_1, &pins1);

    // Cross-route master clocks (SCK/WS) into slave peripheral (I2S1) via internal GPIO matrix
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_SCK]);
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_WS]);
    gpio_matrix_in((uint32_t)AUDIO_SCK, (uint32_t)I2S1I_BCK_IN_IDX, false);
    gpio_matrix_in((uint32_t)AUDIO_WS,  (uint32_t)I2S1I_WS_IN_IDX,  false);

    // Reset peripheral state machines simultaneously for sample-level alignment
    i2s_stop(I2S_NUM_0);
    i2s_stop(I2S_NUM_1);

    REG_SET_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);
    REG_CLR_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);

    // Start slave first so it is primed to lock onto the master's clock instantly
    i2s_start(I2S_NUM_1); 
    i2s_start(I2S_NUM_0);    
}

void I2SAudio::sample() {
    size_t bytes_read0, bytes_read1;
    
    // Block until complete sample frames arrive from DMA ring buffers
    i2s_read(I2S_NUM_0, this->buf0, sizeof(this->buf0), &bytes_read0, portMAX_DELAY);
    i2s_read(I2S_NUM_1, this->buf1, sizeof(this->buf1), &bytes_read1, portMAX_DELAY);
    
    // Right-shift 24-bit left-aligned hardware data down to standard signed 32-bit PCM 
    // and interleave channels into final output buffer
    for (int i = 0; i < AUDIO_SAMPLES; i++) {
        this->buf[i * 4]     = this->buf0[i * 2] >> 8;      // Mic 1 (I2S0 Left)
        this->buf[i * 4 + 1] = this->buf0[i * 2 + 1] >> 8;  // Mic 2 (I2S0 Right)
        this->buf[i * 4 + 2] = this->buf1[i * 2] >> 8;      // Mic 3 (I2S1 Left)
        this->buf[i * 4 + 3] = this->buf1[i * 2 + 1] >> 8;  // Mic 4 (I2S1 Right)
    }
}