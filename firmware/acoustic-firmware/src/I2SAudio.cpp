#include "I2SAudio.h"
#include "Constants.h"


void I2SAudio::init(){
    i2s_config_t i2s_config = {
        .sample_rate = AUDIO_FREQ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, 
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .dma_buf_count = 8,
        .dma_buf_len = 1024,
        .use_apll = false
    };

    i2s_pin_config_t pins1 = {
        .bck_io_num = AUDIO_SCK2, 
        .ws_io_num = AUDIO_WS2,   
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD2
    };

    i2s_pin_config_t pins0 = {
        .bck_io_num = AUDIO_SCK1,
        .ws_io_num = AUDIO_WS1,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = AUDIO_SD1
    };

    // Master: I2S_NUM_0
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pins0);

    // Slave: I2S_NUM_1
    i2s_config.mode = (i2s_mode_t)(I2S_MODE_SLAVE | I2S_MODE_RX);
    i2s_driver_install(I2S_NUM_1, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_1, &pins1);

    // Sync
    i2s_stop(I2S_NUM_0);
    i2s_stop(I2S_NUM_1);

    I2S0.conf.rx_reset = 1; I2S0.conf.rx_reset = 0;
    I2S0.conf.rx_fifo_reset = 1; I2S0.conf.rx_fifo_reset = 0;
    I2S0.lc_conf.in_rst = 1;    I2S0.lc_conf.in_rst = 0;
    
    I2S1.conf.rx_reset = 1; I2S1.conf.rx_reset = 0;
    I2S1.conf.rx_fifo_reset = 1; I2S1.conf.rx_fifo_reset = 0;
    I2S1.lc_conf.in_rst = 1;    I2S1.lc_conf.in_rst = 0;

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

