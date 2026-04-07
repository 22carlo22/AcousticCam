#ifndef DOUBLEBUFFER_H
#define DOUBLEBUFFER_H

#include <Arduino.h>

class DoubleBuffer{
    private:
        uint8_t* buf[2];
        SemaphoreHandle_t empty;
        SemaphoreHandle_t filled;
    public:

        void init(uint32_t buf_len);
        uint8_t* writeRequest();
        void writeComplete(uint8_t* buf);

        uint8_t* readRequest();
        void readComplete(uint8_t* buf);

};

#endif