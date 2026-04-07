#ifndef SCREEN_H
#define SCREEN_H

#include <Arduino.h>
#include <TFT_eSPI.h>

class Screen{
    private: 
        TFT_eSPI tft = TFT_eSPI(); 
        uint16_t* dma_buffer;
        uint64_t strip_size;
    public:

        void init();
        void display(uint16_t *img);
};


#endif