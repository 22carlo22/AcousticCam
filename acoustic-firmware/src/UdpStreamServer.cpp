#include "UdpStreamServer.h"

UdpStreamServer::UdpStreamServer(Cam& cameraInstance, const char* targetIp, uint16_t port)
    : _cam(cameraInstance), _target_ip(targetIp), _port(port), _running(false), _task_handle(NULL) {}

UdpStreamServer::~UdpStreamServer() {
    stop();
}

bool UdpStreamServer::start() {
    if (_running) return true;

    // Setup socket
    if (!_udp.begin(_port)) {
        return false;
    }

    _running = true;


    BaseType_t result = xTaskCreatePinnedToCore(
        UdpStreamServer::taskWorker, 
        "UDP_Stream_Task",           
        4096,                        
        this,                        
        2,                           
        &_task_handle,               
        0                            
    );

    if (result != pdPASS) {
        _udp.stop(); 
        _running = false;
        return false;
    }

    return true;
}

void UdpStreamServer::stop() {
    _running = false;
    _udp.stop(); 

    if (_task_handle != NULL) {
        vTaskDelete(_task_handle);
        _task_handle = NULL;
    }
}

void UdpStreamServer::taskWorker(void* pvParameters) {
    UdpStreamServer* instance = (UdpStreamServer*)pvParameters;
    instance->run();
}

void UdpStreamServer::run() {
    uint8_t frame_id = 0; 

    while (_running) {
        camera_fb_t * fb = _cam.readRequest();

        uint8_t *buffer = fb->buf;
        size_t length = fb->len;
        size_t remaining = length;
        size_t offset = 0;
        uint16_t packet_index = 0;

        uint8_t total_packets = (length + UDP_PACKET_MAX - 1) / UDP_PACKET_MAX;
        uint32_t packet_delay_ms = (length > 35000) ? 2 : 1;

        while (remaining > 0 && _running) {
            size_t chunk_size = (remaining > UDP_PACKET_MAX) ? UDP_PACKET_MAX : remaining;
            _udp.beginPacket(_target_ip, _port);
                
            _udp.write(frame_id);                   // Byte 0: Unique Frame Signature
            _udp.write(total_packets);              // Byte 1: Expected Count
            _udp.write((packet_index >> 8) & 0xFF); // Byte 2: Index High
            _udp.write(packet_index & 0xFF);        // Byte 3: Index Low
            _udp.write((chunk_size >> 8) & 0xFF);   // Byte 4: Chunk High
            _udp.write(chunk_size & 0xFF);          // Byte 5: Chunk Low

            _udp.write(buffer + offset, chunk_size);
            _udp.endPacket();

            offset += chunk_size;
            remaining -= chunk_size;
            packet_index++;


        }
        
        frame_id++; 
        _cam.readComplete(fb);
    }

    _task_handle = NULL;
    vTaskDelete(NULL);
}