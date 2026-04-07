#include <Arduino.h>
#include "Constants.h"
#include "DoubleBuffer.h"
#include "Cam.h"
#include "Screen.h"
#include "Hotspot.h"
#include "I2SAudio.h"


Cam cam = Cam();
Screen screen = Screen();
Hotspot hotspot = Hotspot();
I2SAudio audio = I2SAudio();

int32_t buf[4*AUDIO_SAMPLES];

void setup() {
  Serial.begin(921600);
  audio.init();
  Serial.println("Hello world");
}

void loop() {
  while(Serial.available() == 0) yield();
  Serial.read();

  audio.sample(buf);
  Serial.write((uint8_t*)buf, 4*AUDIO_SAMPLES*sizeof(int32_t));
}

