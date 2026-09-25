#include "SoftAp.h"

SoftAp::SoftAp(const char* ssid, const char* password, const char* ip) {
    this->ssid = ssid;
    this->password = password;
    this->ip = ip;
    // Create FreeRTOS mutex to synchronize TCP port mapping across multiple threads
    this->net_mutex = xSemaphoreCreateMutex();
}

void SoftAp::begin() {
    // Set ESP32 to Access Point mode
    WiFi.mode(WIFI_AP);

    IPAddress local_ip;
    IPAddress gateway;
    IPAddress subnet;
    
    local_ip.fromString(this->ip);
    gateway.fromString(this->ip);
    subnet.fromString("255.255.255.0");
    
    // Apply static IP configuration to AP interface
    if (!WiFi.softAPConfig(local_ip, gateway, subnet)) {
        return;
    }
    
    // Launch SoftAP on Channel 6, hidden=0, max_connections=1
    WiFi.softAP(ssid, password, 6, 0, 1);
}

void SoftAp::startPort(uint16_t port_num) {
    // Acquire network lock before modifying server map
    if (xSemaphoreTake(net_mutex, portMAX_DELAY) != pdTRUE) {
        return;
    }

    // Skip allocation if server port is already initialized
    if (sessions.find(port_num) != sessions.end()) {
        xSemaphoreGive(net_mutex);
        return;
    }

    // Allocate dynamic TCP listener on target port
    WiFiServer* new_tcp_server = new WiFiServer(port_num);
    new_tcp_server->begin();

    PortSession session;
    session.server = new_tcp_server;
    session.client = new WiFiClient();

    sessions[port_num] = session;

    xSemaphoreGive(net_mutex);
}

void SoftAp::send(uint16_t port_num, uint8_t data[], uint16_t len) {
    // Acquire network lock for thread-safe socket operations
    if (xSemaphoreTake(net_mutex, portMAX_DELAY) != pdTRUE) {
        return;
    }

    // Exit early if the requested port does not exist in sessions map
    auto it = sessions.find(port_num);
    if (it == sessions.end()) {
        xSemaphoreGive(net_mutex);
        return;
    }

    PortSession& session = it->second;

    bool is_session_valid = (session.client != nullptr) && (session.server != nullptr);
    if (!is_session_valid) {
        xSemaphoreGive(net_mutex);
        return;
    }

    // Verify socket connection state
    bool is_connected = *(session.client) && session.client->connected();
    if (!is_connected) {
        bool has_stale_socket = static_cast<bool>(*(session.client));
        if (has_stale_socket) {
            session.client->stop();
        }

        // Poll server for a fresh incoming TCP client connection
        *(session.client) = session.server->available();
        
        bool is_reconnected = *(session.client) && session.client->connected();
        if (!is_reconnected) {
            xSemaphoreGive(net_mutex);
            return;
        }

        // Disable Nagle's algorithm for low-latency frame transmission
        session.client->setNoDelay(true);
    }

    // Write 2-byte Big Endian length prefix header followed by payload block
    session.client->write((len >> 8) & 0xFF);
    session.client->write(len & 0xFF);
    session.client->write(data, len);

    xSemaphoreGive(net_mutex);
}