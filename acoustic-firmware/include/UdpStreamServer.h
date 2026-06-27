#ifndef UDP_STREAM_SERVER_H
#define UDP_STREAM_SERVER_H

#include <Arduino.h>
#include <WiFiUdp.h>
#include "Cam.h"

class UdpStreamServer {
public:
    UdpStreamServer(Cam& cameraInstance, const char* targetIp, uint16_t port);
    ~UdpStreamServer();
    bool start();
    void stop();

private:
    static void taskWorker(void* pvParameters);
    void run(); 

    Cam& _cam;                // Assumes that the cam is fomratted as QVGA and JPEG
    const char* _target_ip;
    uint16_t _port;
    WiFiUDP _udp;
    
    bool _running;
    TaskHandle_t _task_handle;

    static const size_t UDP_PACKET_MAX = 1400; 
};

#endif