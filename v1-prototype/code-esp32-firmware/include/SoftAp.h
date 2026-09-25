#ifndef SOFTAP_H
#define SOFTAP_H

#include <Arduino.h>
#include <WiFi.h>
#include <unordered_map>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

/**
 * @brief Thread-safe SoftAP streaming class supporting multi-port TCP transmission.
 *
 * Configures an ESP32 Wi-Fi Access Point and manages multiple persistent TCP server
 * endpoints. Utilizes FreeRTOS semaphores to ensure thread-safe socket reads and writes 
 * across concurrent streaming tasks. Designed for single-client high-throughput streaming.
 */
class SoftAp {
private:
    const char* ssid;
    const char* password;
    const char* ip;
    
    /**
     * @brief Container managing persistent socket server and client references per port.
     */
    struct PortSession {
        WiFiServer* server = nullptr;
        WiFiClient* client = nullptr;
    };

    /** Map pairing port numbers to active TCP socket sessions. */
    std::unordered_map<uint16_t, PortSession> sessions;
    
    /** FreeRTOS mutex synchronizing network calls across concurrent task routines. */
    SemaphoreHandle_t net_mutex;

public:
    /**
     * @brief Constructs a SoftAp instance and initializes the thread synchronization mutex.
     * 
     * @param ssid AP Network SSID string.
     * @param password AP Network WPA2 password string.
     * @param ip Local static IP address string (also serves as default gateway).
     */
    SoftAp(const char* ssid, const char* password, const char* ip);

    /**
     * @brief Configures static IP settings and starts the Wi-Fi Access Point broadcast.
     */
    void begin();

    /**
     * @brief Initializes a TCP server on a target port and binds a session entry.
     * 
     * @param port_num Target network port to open for client connections.
     */
    void startPort(uint16_t port_num);

    /**
     * @brief Transmits a 2-byte length-prefixed payload frame over a designated TCP port.
     * 
     * Handles automatic client connection polling, stale socket cleanup, and 
     * low-latency byte transmission under mutex lock protection.
     * 
     * @param port_num Target port number corresponding to an active session.
     * @param data Pointer to raw byte array payload.
     * @param len Number of bytes to transmit.
     */
    void send(uint16_t port_num, uint8_t data[], uint16_t len);
};

#endif // SOFTAP_H