#include <Arduino.h>
#include "Constants.h"
#include "Cam.h"
#include "I2SAudio.h"
#include "UdpStreamServer.h"
#include <WiFi.h>

I2SAudio audio = I2SAudio();
int32_t buf[4*AUDIO_SAMPLES];

Cam camera;
UdpStreamServer udpServer(camera, UDP_IP, UDP_SOCKET);

void setup() {
  Serial.begin(921600);

  audio.init();
  camera.init();

  WiFi.begin(WIFI_ID, WIFI_PASSWORD);
    
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi Connected successfully!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  udpServer.start();

}

void loop() {
  while(Serial.available() == 0) delay(1);

  switch(Serial.read()){
    case REQ_AUDIO_DATA:
        audio.sample(buf);
        Serial.write((uint8_t*)buf, 4*AUDIO_SAMPLES*sizeof(int32_t));
        break;
  }
}