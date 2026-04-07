#include "Screen.h"

#include <SPI.h>
#include "Constants.h"

void Screen::init(){
    tft.init();
    tft.setRotation(ORIENTATION);
    tft.initDMA();
    strip_size = CAM_WIDTH * STRIP_HEIGHT * sizeof(uint16_t);
    dma_buffer = (uint16_t*)heap_caps_malloc(strip_size, MALLOC_CAP_DMA);
}

void Screen::display(uint16_t* img){
    uint16_t* src_ptr = img;
    for (int y = 0; y < CAM_HEIGHT; y += STRIP_HEIGHT) {
        
        while (tft.dmaBusy()) yield();

        memcpy(dma_buffer, src_ptr, strip_size);

        tft.startWrite();
        tft.pushImageDMA(0, y, CAM_WIDTH, STRIP_HEIGHT, dma_buffer);
        tft.endWrite();

        src_ptr += (CAM_WIDTH * STRIP_HEIGHT);
    }

}