#include "I2SAudio.h"
#include "Constants.h"
#include "driver/gpio.h"
#include "soc/system_reg.h"        

void I2SAudio::init() {
    // Setup I2S parameters 
    i2s_config_t i2s_config = {
        .sample_rate = AUDIO_FREQ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, 
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,     
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = AUDIO_SAMPLES,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // Make I2S_NUM_0 master
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);

    i2s_pin_config_t pins0 = {
        .bck_io_num = AUDIO_SCK,        
        .ws_io_num = AUDIO_WS,          
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD1        
    };
    i2s_set_pin(I2S_NUM_0, &pins0);

    // Make I2S_NUM_1 slave
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_SLAVE | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);

    i2s_pin_config_t pins1 = {
        .bck_io_num = I2S_PIN_NO_CHANGE, 
        .ws_io_num = I2S_PIN_NO_CHANGE,  
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD2         
    };
    i2s_set_pin(I2S_NUM_1, &pins1);

    // Attach master clock into the slave peripheral
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_SCK]);
    PIN_INPUT_ENABLE(GPIO_PIN_MUX_REG[AUDIO_WS]);
    gpio_matrix_in((uint32_t)AUDIO_SCK, (uint32_t)I2S1I_BCK_IN_IDX, false);
    gpio_matrix_in((uint32_t)AUDIO_WS,  (uint32_t)I2S1I_WS_IN_IDX,  false);

    // Sync
    i2s_stop(I2S_NUM_0);
    i2s_stop(I2S_NUM_1);

    REG_SET_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);
    REG_CLR_BIT(SYSTEM_PERIP_RST_EN1_REG, SYSTEM_I2S0_RST | SYSTEM_I2S1_RST);

    i2s_start(I2S_NUM_1); 
    i2s_start(I2S_NUM_0);    
}

void I2SAudio::sample(int32_t *buf){
    static int32_t buf0[2*AUDIO_SAMPLES], buf1[2*AUDIO_SAMPLES];
    size_t bytes_read0, bytes_read1;
    
    i2s_read(I2S_NUM_0, buf0, 2 * AUDIO_SAMPLES * sizeof(int32_t), &bytes_read0, portMAX_DELAY);
    i2s_read(I2S_NUM_1, buf1, 2 * AUDIO_SAMPLES * sizeof(int32_t), &bytes_read1, portMAX_DELAY);
    
    for (int i = 0; i < AUDIO_SAMPLES; i++ ) {
        buf[i*4]     = buf0[i*2] >> 8;     
        buf[i*4 + 1] = buf0[i*2 + 1] >> 8; 
        buf[i*4 + 2] = buf1[i*2] >> 8;     
        buf[i*4 + 3] = buf1[i*2 + 1] >> 8; 
    }
}


