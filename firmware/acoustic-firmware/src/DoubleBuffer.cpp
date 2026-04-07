#include "DoubleBuffer.h"

void DoubleBuffer::init(uint32_t buf_len){
    buf[0] = (uint8_t*) ps_malloc(buf_len);
    buf[1] = (uint8_t*) ps_malloc(buf_len);

    empty = xQueueCreate(2, sizeof(uint8_t*));
    filled = xQueueCreate(2, sizeof(uint8_t*));

    xQueueSend(empty, &buf[0], 0);
    xQueueSend(empty, &buf[1], 0);
}

uint8_t* DoubleBuffer::writeRequest(){
    uint8_t* data; 
    xQueueReceive(empty, &data, portMAX_DELAY);
    return data;
}


void DoubleBuffer::writeComplete(uint8_t* data){
    xQueueSend(filled, &data, portMAX_DELAY);
}

uint8_t* DoubleBuffer::readRequest(){
    uint8_t* data;
    xQueueReceive(filled, &data, portMAX_DELAY);
    return data;

}

void DoubleBuffer::readComplete(uint8_t* data){
    xQueueSend(empty, &data, portMAX_DELAY);   
}