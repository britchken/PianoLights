#!/usr/bin/env python
import sys
import os
import pygame
import pygame.midi
import random
import serial
import math
from time import sleep

from pygame.locals import *

import socket
s = socket.socket()
host = '10.0.0.65'
port = 12345

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

ser = serial.Serial('/dev/tty.usbmodem14201', baudrate=9600)
print(ser.name)

# Change this to override use of default input device
device_id = 0
if device_id is None:
    input_id = pygame.midi.get_default_input_id()
else:
    input_id = device_id
print ("Using input_id: %s" % input_id)
inn = pygame.midi.Input( input_id )
print ("Logging started:")


def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1]

color_stack = []
counter = [300]*88
while True:

    counter = [i + 1 for i in counter]
    expired = [i for (i,j) in enumerate(counter) if counter[i] == 200]
    for i in expired:
        #print(str(i) + " expired!")
        if i in color_stack:
            color_stack.remove(i)

    events = event_get()
    for e in events:
        if e.type in [pygame.midi.MIDIIN]:
            if (e.data2 > 0) and (e.data1 >= 21) and (e.data1 <= 108):
                key = e.data1 - 21
                counter[key] = 0
                # if key is not in the stack and it is a key PRESS (not release)
                if not key in color_stack and e.status == 144:
                    #print ("Timestamp: " + str(e.timestamp) + "ms, Channel: " + str(e.data1) + ", Value: " + str(e.data2))
                    color_stack.append(key)
                else:
                    if key in color_stack:
                        color_stack.remove(key)

    # if there are new data from the MIDI controller
    if inn.poll():
        midi_events = inn.read(1024)
        midi_evs = pygame.midi.midis2events(midi_events, inn.device_id)
        for m_e in midi_evs:
            event_post( m_e )

    if (14 in color_stack) and (77 in color_stack) and len(color_stack) == 2:
        ser.write(to_bytes(1, 1))
        sleep(1)
        s.connect((host, port))
        sys.exit(0)
    elif (len(color_stack) > 0):
        key = int(255-(color_stack[-1])*2.8) # 2.3 is arbitrary number for color
        ser.write(to_bytes(key, 1))
    else:
        ser.write(to_bytes(0, 1))
    sleep(0.025)
