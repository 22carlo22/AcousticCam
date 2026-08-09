#include "SoftAp.h"

// Constructor: Stores network credentials into private member attributes
SoftAp::SoftAp(const char* ssid, const char* password) {
    this->ssid = ssid;
    this->password = password;
}

// Configures and activates the ESP32 Soft Access Point mode
void SoftAp::begin() {
    // 1. Explicitly switch radio mode to Access Point
    WiFi.mode(WIFI_AP);
    
    // 2. Configure static IP address range
    if (!WiFi.softAPConfig(local_IP, gateway, subnet)) {
        return;
    }
    
    // 3. Launch Access Point beacon broadcast (Channel 6, Hidden: 0, Max Connections: single client)
    WiFi.softAP(ssid, password, 6, 0, 1);
}

// Allocates and binds a new WiFiUDP socket instance to map registry
void SoftAp::startPort(uint16_t port_num) {
    // Check if port was already registered to prevent memory leak
    if (ports.find(port_num) != ports.end()) {
        return;
    }

    // Allocate dynamic memory for new socket instance
    WiFiUDP* new_udp_socket = new WiFiUDP();
    
    // Bind socket to network port
    if (new_udp_socket->begin(port_num)) {
        ports[port_num] = new_udp_socket;
    } else {
        delete new_udp_socket; // Clean up allocated heap memory on binding failure
    }
}

// Looks up socket in registry map and streams fragmented chunk packets over UDP
void SoftAp::send(uint16_t port_num, uint8_t id, uint8_t data[], uint16_t len) {
    // 1. Lookup safe check: verify that port was initialized via startPort()
    auto it = ports.find(port_num);
    if (it == ports.end()) {
        return;
    }

    WiFiUDP* active_udp = it->second;

    size_t remaining = len;
    size_t offset = 0;
    uint16_t packet_index = 0;

    // Calculate required fragment count based on maximum MTU payload size limit (1400 bytes)
    uint8_t total_packets = (len + UDP_PACKET_MAX - 1) / UDP_PACKET_MAX;

    // Slice payload and stream packets sequentially
    while (remaining > 0) {
        size_t chunk_size = (remaining > UDP_PACKET_MAX) ? UDP_PACKET_MAX : remaining;
        
        // Open packet connection target toward destination client IP
        active_udp->beginPacket(TARGET_IP, port_num);
            
        // Write 6-byte packet header:
        active_udp->write(id);                          // Byte 0: Sequence ID
        active_udp->write(total_packets);                // Byte 1: Total Packets
        active_udp->write((packet_index >> 8) & 0xFF);   // Byte 2: Fragment Index High
        active_udp->write(packet_index & 0xFF);          // Byte 3: Fragment Index Low
        active_udp->write((chunk_size >> 8) & 0xFF);     // Byte 4: Chunk Length High
        active_udp->write(chunk_size & 0xFF);            // Byte 5: Chunk Length Low
        
        // Append raw payload chunk
        active_udp->write(data + offset, chunk_size);

        // Hardware transmission flushing check
        if (active_udp->endPacket() == 0) {
            // Buffer busy or transmitter clogged: back off and retry fragment
            delay(1);
            continue; 
        }

        // Advance buffer indices upon successful transmission
        offset += chunk_size;
        remaining -= chunk_size;
        packet_index++;
    }
}