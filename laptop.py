#!/usr/bin/env python
import sys
import os
import pygame
import pygame.midi
import colorsys
import random
import serial
import math

def get_N_HexCol(N):

    HSV_tuples = [(0.5*x/N, 1, 1) for x in xrange(N)]
    hex_out = []
    
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x*255),colorsys.hsv_to_rgb(*rgb))
        hex_out.append(rgb)
    return hex_out


colors = get_N_HexCol(88)

ser = serial.Serial('COM3')
print(ser.name)

from pygame.locals import *
# display a list of MIDI devices connected to the computer
def print_device_info():
    for i in range( pygame.midi.get_count() ):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r
        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"
        print ("%2i: interface: %s, name: %s, opened: %s %s" %
               (i, interf, name, opened, in_out))
pygame.init()
pygame.fastevent.init()
event_get = pygame.fastevent.get
event_post = pygame.fastevent.post
pygame.midi.init()
print ("Available MIDI devices:")
print_device_info();
# Change this to override use of default input device
device_id = None
if device_id is None:
    input_id = pygame.midi.get_default_input_id()
else:
    input_id = device_id
print ("Using input_id: %s" % input_id)
i = pygame.midi.Input( input_id )
print ("Logging started:")
going = True

pressed = [0]*109


#Animation
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (15,40)
windowSurface = pygame.display.set_mode((1400, 800), 0, 32)
pygame.display.set_caption('Piano lights!')
BLACK = (30, 30, 30)
windowSurface.fill(BLACK)
pygame.display.update()

while going:
    events = event_get()
    for e in events:
        if e.type in [QUIT]:
            going = False
        if e.type in [KEYDOWN]:
            going = False
        if e.type in [pygame.midi.MIDIIN]:
            # print information to console
            if (e.data2 > 0) and (e.data1 != 64) and (e.data1 >= 21) and (e.data1 <= 108):
                #Pos and col for drawing on laptop
                pos = (int(round((e.data1 - 21) * 1400 / 88)), int(round(700 - 5 * e.data2)))
                col = colors[int(e.data1 - 21)]
                if not pressed[e.data1]:
                    print ("Timestamp: " + str(e.timestamp) + "ms, Channel: " + str(e.data1) + ", Value: " + str(e.data2))
                    pressed[e.data1] = 1
                    pygame.draw.circle(windowSurface, col, pos, 8, 0)
                    ser.write(chr(e.data1 - 21))
                else:
                    pressed[e.data1] = 0
                    ser.write(chr(e.data1 - 21 + 88))
                    pygame.draw.rect(windowSurface, BLACK, (pos[0]-8, 0, 16, 800), 0)
                    if e.data1 == 21:
                        pygame.draw.rect(windowSurface, BLACK, (0, 0, 1400, 800), 0)
                        pressed = [0] * 109
                        print("CLEAR")
                        
                pygame.display.update()
                    
    # if there are new data from the MIDI controller
    if i.poll():
        midi_events = i.read(10)
        midi_evs = pygame.midi.midis2events(midi_events, i.device_id)
        for m_e in midi_evs:
            event_post( m_e )
