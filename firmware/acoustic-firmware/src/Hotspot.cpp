#include "Hotspot.h"
#include "Arduino.h"
#include "Constants.h"

void Hotspot::init(){
    for(uint16_t n = 0; n < 256; n++){
        uint16_t r = (n > 127) ? (n - 127) >> 2 : 0;       
        uint16_t g = (n < 128) ? (n >> 1) : (255 - n) >> 1; 
        uint16_t b = (n < 128) ? (127 - n) >> 2 : 0; 
        rgb_map[n*3 + 0] = r;
        rgb_map[n*3 + 1] = g;
        rgb_map[n*3 + 2] = b;
    }
}


void Hotspot::apply(uint16_t *img, int32_t* sound){
    static const int32_t INTENSITY_MIN = NOISE_BASE;
    static const int32_t INTENSITIY_MAX = INTENSITY_MIN + (1 << NOISE_RANGE_SCALE) - 1;

    static const uint16_t PIXEL_XMAX = CAM_WIDTH/SEARCH_GRID_WIDTH;
    static const uint16_t PIXEL_YMAX = CAM_HEIGHT/SEARCH_GRID_HEIGHT;

    for(uint16_t y = 0; y < SEARCH_GRID_HEIGHT; y++){
        for(uint16_t x = 0; x < SEARCH_GRID_WIDTH; x++){
            int32_t intensity = sound[x + y*SEARCH_GRID_WIDTH];
            if(intensity < INTENSITY_MIN)  continue;

            if(intensity > INTENSITIY_MAX ) intensity = INTENSITIY_MAX;
            intensity -= INTENSITY_MIN; 
            
            uint8_t normalized;
            #if (NOISE_RANGE_SCALE < 8)
                normalized = intensity << (8-NOISE_RANGE_SCALE); 
            #else
                normalized = intensity >> (NOISE_RANGE_SCALE-8);
            #endif 
            
            uint8_t r1 = rgb_map[normalized*3+0];
            uint8_t g1 = rgb_map[normalized*3+1];
            uint8_t b1 = rgb_map[normalized*3+2];

            for(uint16_t pixel_y = 0; pixel_y < PIXEL_YMAX; pixel_y++){
                for(uint16_t pixel_x = 0; pixel_x < PIXEL_XMAX; pixel_x++){
                    uint16_t img_i = (pixel_x+x*PIXEL_XMAX) + (pixel_y+y*PIXEL_YMAX)*CAM_WIDTH;
                    uint16_t color565 = img[img_i];

                    uint8_t r2 = (color565 >> 11) & 0x1F;
                    uint8_t g2 = (color565 >> 5) & 0x3F;
                    uint8_t b2 = color565 & 0x1F;

                    uint8_t out_r = ((256-ALPHA)*r1 + (ALPHA)*r2) >> 8;
                    uint8_t out_g = ((256-ALPHA)*g1 + (ALPHA)*g2) >> 8;
                    uint8_t out_b = ((256-ALPHA)*b1 + (ALPHA)*b2) >> 8;

                    color565 = (out_r << 11) | (out_g << 5) | out_b;
                    img[img_i] = color565;
                }
            }

        }
    }

}
