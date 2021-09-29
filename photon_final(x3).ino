// This #include statement was automatically added by the Particle IDE.
#include <neopixel.h>

#include "application.h"
// #include "neopixel.h" // use for local build

SYSTEM_MODE(AUTOMATIC);

#define PIXEL_PIN D2
#define PIXEL_COUNT 450
#define PIXEL_TYPE WS2812B

Adafruit_NeoPixel strip = Adafruit_NeoPixel(PIXEL_COUNT, PIXEL_PIN, PIXEL_TYPE);

uint32_t pixels[PIXEL_COUNT];

int head;
int lock;
int goingup, cc, bb;

void setup()
{
    pinMode(D5, OUTPUT);
    Serial.begin(9600);
    strip.begin();
    strip.setBrightness(120);
    strip.show(); // Initialize all pixels to 'off'
    head = 0;
    cc = 84;
    goingup = 0;
    bb = 80;
    digitalWrite(D5, HIGH);
}

int i, j;

void serialEvent()
{
    byte new_data;
    new_data = Serial.read();
    if (new_data == 1) {
        strip.setBrightness(0);
        strip.show();
        delay(2000);
        digitalWrite(D5, LOW);
        while (1) {
            delay(40);
            
            if (goingup) {
                bb = bb + 1;
                if (bb == 60) {
                    goingup = 0;
                }
            } else {
                bb = bb - 1;
                if (bb == 17) {
                    goingup = 1;
                }
            }
            
            for (i = 0; i < PIXEL_COUNT; i = i + 1) {
                strip.setBrightness(bb);
                strip.setPixelColor(i, Wheel(cc));
            }
            strip.show();
        }
    }
    pixels[head] = Wheel(new_data);
    
    //Old "loop"
    head = head + 1;
    if (head == PIXEL_COUNT) {
        head = 0;
    }
    i = 0;
    j = i + head;
    if (j >= PIXEL_COUNT) {
        j = j - PIXEL_COUNT;
    }
    while (i != PIXEL_COUNT) {
        j = j + 1;
        i = i + 1;
        if (j == PIXEL_COUNT) {
            j = 0;
        }
        strip.setPixelColor(PIXEL_COUNT-i-1, pixels[j]);
    }
    strip.show();
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  if(WheelPos == 0) {
    return strip.Color(0, 0, 0);
  }
  if(WheelPos < 85) {
   return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if(WheelPos < 170) {
   WheelPos -= 85;
   return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
   WheelPos -= 170;
   return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}

