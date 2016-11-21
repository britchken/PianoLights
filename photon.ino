// This #include statement was automatically added by the Particle IDE.
#include "neopixel/neopixel.h"
#include "application.h"
// #include "neopixel.h" // use for local build

SYSTEM_MODE(AUTOMATIC);

#define PIXEL_PIN D2
#define PIXEL_COUNT 150
#define PIXEL_TYPE WS2812B

Adafruit_NeoPixel strip = Adafruit_NeoPixel(PIXEL_COUNT, PIXEL_PIN, PIXEL_TYPE);

int keys_held;

typedef struct blast {
    int16_t pos;
    int16_t end_pos;
    byte key;
    uint32_t col;
    struct blast *next;
} blast_t;

blast_t *head;
blast_t *tail;
blast_t *newguy;
blast_t *curr;
blast_t *temp;

void construct(struct blast *me, byte key) {
    me->pos = 149;
    me->end_pos = -10;
    me->key = key;
    me->col = Wheel(176 - key * 2);
    me->next = NULL;
}

void setup()
{
    Serial.begin(9600);
    strip.begin();
    strip.setBrightness(255);
    strip.show(); // Initialize all pixels to 'off'

    head = NULL;
    tail = NULL;
    newguy = NULL;

}

void serialEvent()
{
    byte new_data;
    new_data = Serial.read();

    if (head == NULL) {
        keys_held = keys_held + 1;
        newguy = (blast_t*) malloc(sizeof(blast_t));
        construct(newguy, new_data);
        head = newguy;
        tail = newguy;
    } else {
        
        newguy = head;
        while (1)
        {
            //If this serial event is letting go of a key
            if ( newguy == NULL || ((newguy->key == new_data - 88) && (newguy->end_pos == -10))) {
                keys_held = keys_held - 1;
                if (keys_held == 0) {
                    newguy->end_pos = 149;
                }
                break;
            }
            
            //Otherwise, this serial event is pressing a key
            if (newguy->next == NULL) {
                keys_held = keys_held + 1;
                newguy = (blast_t*) malloc(sizeof(blast_t));
                construct(newguy, new_data);
                tail->next = newguy;
                tail = newguy;
                break;
            }
            newguy = newguy->next;
        }
    }
    //Serial.printlnf("Created node, the color is: %d, %d, %d", newguy->r, newguy->g, newguy->b);
}

void loop()
{
    curr = head;
    int16_t temp_pos, end_temp_pos;
    while(curr != NULL) {

        temp_pos = curr->pos;
        end_temp_pos = curr->end_pos;
        
        //Write color
        if (temp_pos >= 0) {
            curr->pos = temp_pos - 1;
            strip.setPixelColor(149 - temp_pos, curr->col);
        }
        
        //Erase
        if (end_temp_pos >= 0) {
            curr->end_pos = end_temp_pos - 1;
            strip.setPixelColor(149 - end_temp_pos, strip.Color(0, 0, 0));
            
            //Delete link if necessary
            if (end_temp_pos == 0) {
                if (curr == tail) {
                    tail = NULL;
                }
                temp = curr->next;
                free(curr);
                head = temp;
            }
        }
    
        //Iterate the while loop
        curr = curr->next;
    }
    strip.show();
    delay(25);
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
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

