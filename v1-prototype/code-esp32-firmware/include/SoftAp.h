#ifndef SOFTAP_H
#define SOFTAP_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <unordered_map>

/**
 * @brief Manages the ESP32 Wi-Fi Access Point (SoftAP) and streams fragmented UDP packet frames for a single client.
 */
class SoftAp {
    private:
        IPAddress local_IP{192, 168, 4, 1};  // Access point local gateway address
        IPAddress gateway{192, 168, 4, 1};  
        IPAddress subnet{255, 255, 255, 0};

        static const uint16_t UDP_PACKET_MAX = 1400; // Payload size cap per UDP fragment (under standard 1500 MTU)
        const char* TARGET_IP = "192.168.4.2";       // Fixed destination client address (laptop/host PC)

        const char* ssid;
        const char* password;
        std::unordered_map<uint16_t, WiFiUDP*> ports; // Registry mapping port numbers to active socket instances

    public:
        /**
         * @brief Constructs a SoftAp manager instance.
         * @param ssid AP Network SSID name.
         * @param password AP Network password.
         */
        SoftAp(const char* ssid, const char* password);

        /**
         * @brief Configures interface subnet, assigns static IP, and begins SoftAP beacon broadcasting.
         */
        void begin();

        /**
         * @brief Dynamically allocates and binds a UDP socket to a target port number.
         * @param port_num Port index to open and bind.
         */
        void startPort(uint16_t port_num);
        
        /**
         * @brief Slices raw binary payloads into structured MTU fragments and streams them over UDP.
         * @param port_num Target destination UDP port mapped in registry.
         * @param id Sequential frame identifier counter.
         * @param data Pointer to raw payload array.
         * @param len Total length of binary payload in bytes.
         */
        void send(uint16_t port_num, uint8_t id, uint8_t data[], uint16_t len);
};

#endif