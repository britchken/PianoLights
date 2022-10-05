# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 13:41:32 2022

@author: I am a skilled comedian
"""

from functools import total_ordering

import queue
import sys
import os
import pygame
import pygame.midi
import random
import serial
import serial.tools.list_ports
import math
from time import sleep
import time
import struct
import json
import binascii

from pygame.locals import *

## REPLACE SOCKET CODE WITH LOCAL CODE SHIT
#import socket
#s = socket.socket()
inMIDI  = None
outMIDI = None
def handle_midi_device():
    print("Possible MIDI Candidates")
    global inMIDI, outMIDI
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) =r
        in_out = ""
        if input:
            in_out += "(input)"
        if output:
            in_out += "(output)"
        pre="   "
        if b'Roland FP' in name:
            if input:
                inMIDI = pygame.midi.Input(i)
            if output:
                pass
                #pygame.midi.Ouput(i)
            pre=">> "
        print(f"{pre}{i}: interface: {interf}, name: {name}, opened: {opened}, in_out: {in_out}")
    print()

ser = None
def handle_serial_device():
    global ser
    print('Possible Serial Candidates')
    for c in serial.tools.list_ports.comports():
        (port, desc, hwid) = c
        pre='   '
        if 'VID:PID=2B04:C00' in hwid:
            if ser is None:
                ser = serial.Serial(port = c.device, baudrate=921600)
                pre='>> '
        print(f"{pre}port: {port}, desc: {desc}, hwid: {hwid}")
        
        
    print()


pygame.init()
pygame.fastevent.init()

event_get  = pygame.fastevent.get
event_post = pygame.fastevent.post
import pyautogui

pygame.midi.init()

print()

# setup everything in these nice neat little functions
# I call them Dwarf functions because they so tiny
handle_serial_device()
handle_midi_device()
if ser is None or inMIDI is None:
    print('No Serial to speak of, quitting...')
    exit()
if inMIDI is None:
    print('No MIDI to speak of, quitting...')
    ser.close()
    exit()

color_stack = []
counter = [300]*88
three_sec_counter = 0

running = True
keyState = [{'p': 0, 't': 0, 'r': 0, 'c': [0,0,0]} for x in range(0, 128)]
keyStateChange = False
keysDown = 0
secretModeRunning = False
x = 0
d = 1
currentStrip = [[0,0,0]for i in range(0,450)]
disco_ball = 0

def blaStrip (fullStrip):
    global ser
    sequence = b'\x4C'
    for c in fullStrip:
        newSeq = bytes(c)
        sequence += newSeq
    ser.write(sequence)
    #ser.write(b'\x00\x00\x00')
    return True

def clearip(): 
    global currentStrip
    currentStrip = [[0,0,0]for i in range(0,450)]

def thingThatGoBackAndForthForTesting():
    global x
    global d
    global currentStrip
    currentStrip[x] = [255,255,255]
    x += d
    if x >= 449:
        d = -1
        x = 449
    if x <= 0:
        d = 1
        x = 0

def randomPoints():
    global keyState
    global currentStrip
    
    for k in keyState:
        if k['p'] == 0:
            continue
        currentStrip[k['r']] = k['c']

src_buff = [[0,0,0] for x in range(0,450)]
og_buff = [[0,0,0] for x in range(0, 450)]

specialDecay = 0.07
normalDecay = 0.9
normalNeighboralygiveaway = 0.7

def colorDecay(color, decay):
    return [int(color[0]*decay), int(color[1]*decay), int(color[2]*decay)]
def colorAdd(color1, color2):
    return [int(color1[0] + color2[0]), int(color1[1] + color2[1]), int(color1[2]+color2[2])]
def colorAddAnDecay(color1, color2, color1Decay):
    coloredDecayed = colorDecay(color1, color1Decay)
    return colorAdd(coloredDecayed, color2)

def secretMode():
    global src_buff
    global og_buff
    global currentStrip
    interval =  int(time.time()*100) & 0x1ff # goes from 0 to 512
    if (interval > 0xff):
        interval = 0x1ff - interval
    
    if disco_ball:
        currentStrip = [[interval, 0, 0] for x in range(0,450)]
    else:
        currentStrip = [[0, 0, 0] for x in range(0,450)]

def wavesFromPoints():
    global src_buff
    global og_buff
    global currentStrip
    temp_buff = [[0,0,0] for x in range(0,450)]
    temp_buff2 = [[0,0,0] for x in range(0,450)]
    og_buff = [colorDecay(c, 0.65) for c in og_buff]

    for k in keyState:
        if k['p'] == 0:
            continue
        #k['p']
        #k['r'] // location
        #k['c'] // color
        # src_buff[k['r']] = [k['p'], k['c']]
        # going laong the array of 450 leds...
        # og_buff has our last c from the leds...
        # temp_buff is to use for temp stuff
        
        # move through temp_buff with src_buff stuff
        index = k['r']
        color = k['c']
        #decayAway = 0.5
        #og_color = k['c']

        someRocker = k['p']*specialDecay / 128

        temp_buff[index] = colorDecay(color, someRocker) # colorGrow(color, currently is, Some growth thing ...)
        if index > 0:
            temp_buff[index-1] = colorDecay(color, someRocker*2)
        if index > 1:
            temp_buff[index-2] = colorDecay(color, someRocker*3)

        if index < 449:
            temp_buff[index+1] = colorDecay(color, someRocker*2)
        if index < 448:
            temp_buff[index+2] = colorDecay(color, someRocker*3)

        # temp_buff lets filll wiht all the key hits by their location
        # 2 iteration of them affecting their neighbor Special case

        # og_buff -> decay by some arbitrary decay -> add temp_buff to og_buff
    for i in range(0, 450):
        temp_buff[i] = colorAddAnDecay(og_buff[i], temp_buff[i], normalDecay)

    og_buff = [[0,0,0] for i in range(0,450)]

    # convolute?
    for i in range(0, 449):
        temp_buff2[i] = colorDecay(temp_buff[i], (1-(normalNeighboralygiveaway*0.99)))
        if i > 0:
            temp_buff2[i] = colorAddAnDecay(temp_buff[i-1], temp_buff2[i], normalNeighboralygiveaway)  
        if i < 449:
            temp_buff2[i] = colorAddAnDecay(temp_buff[i+1], temp_buff2[i], normalNeighboralygiveaway)

    og_buff = [[r if r < 256 else 255, g if g < 256 else 255, b if b < 256 else 255] for [r, g, b] in temp_buff2]

        # move through og_buff and add to src_buff stuff (with decay)
    currentStrip = og_buff


def genColor(key):
    color = int(key*255/87)
    if (color == 0):
        out = [0, 0, 0]
    if (color<85):
        out = [color*3, 255 - color*3, 0]
    elif (color<170):
        color -= 85
        out = [255 - color*3, 0, color*3]
    else:
        color -= 170
        out = [0, color*3, 255-color*3]
    return out

def genPosition(key):
    pos = int(key*449/87)
    return pos


# Turn off sexy mode
ser.write(b'\x4D\x00')
secretModeRunning = False
disco_ball = 0
play_pause = 0
three_sec_counter = 0

while running:
    try:
        clearip()
        #thingThatGoBackAndForthForTesting()
        #randomPoints()
        if secretModeRunning:
            secretMode()
        else:
            wavesFromPoints()
        blaStrip(currentStrip)
        
        events = event_get()
        for e in events:
            if e.type in [pygame.midi.MIDIIN]:
                if e.status == 248:
                    continue
                if e.status >= 144 and e.status <= 159:
                    # 'Note On'k
                    if keyState[e.data1]['p']  != e.data2:
                        key = e.data1-21 # goes from 0 to 87
                        keyState[e.data1]['p']  = e.data2
                        keyState[e.data1]['t'] = time.time()
                        keyState[e.data1]['c'] = genColor(key)
                        keyState[e.data1]['r'] = genPosition(key)

                        keyStateChange = True
                        keysDown += 1
                elif e.status >= 128 and e.status <= 143:
                    # 'Note off'
                    if keyState[e.data1]['p']  != 0:
                        keyState[e.data1]['p']  = 0
                        keyState[e.data1]['t'] = time.time();
                        keyState[e.data1]['c'] = [0,0,0]
                        
                        keyStateChange = True
                        keysDown -= 1

        if keyStateChange:
            keyStateChange = False

        # Turn on
        if (keyState[14+21]['p']  != 0) and (keyState[77+21]['p'] != 0) and keysDown == 2:     
            if not secretModeRunning:
                print('Starting counter')
                secretModeRunning = True
                three_sec_counter = time.time()
        
        # 3 seconds
        if three_sec_counter + 1 < time.time() and three_sec_counter > 0 and play_pause == 0:
            pyautogui.press('playpause')
            play_pause = 1
        
        
        if three_sec_counter + 3 < time.time() and three_sec_counter > 0 and disco_ball == 0:
            print('Starting Super Secret Sexy Mode')
            ser.write(b'\x4D\x11')
            disco_ball = 1
            
        # Turn off
        if (keyState[14+21]['p']  != 0) and (keyState[78+21]['p'] != 0) and keysDown == 2:
            if secretModeRunning:
                print('Stopping Super Secret Sexy Mode')
                ser.write(b'\x4D\x00')
                secretModeRunning = False
                disco_ball = 0
                three_sec_counter = 0
            #print(ser.read_until(b'\n'))

        if inMIDI.poll():
            midiRawEvent = inMIDI.read(1024)
            #print(midiRawEvent)
            midiEvents = pygame.midi.midis2events(midiRawEvent, inMIDI.device_id)
            for midiEvent in midiEvents:
                event_post(midiEvent)
        
        sleep(0.001)
    except KeyboardInterrupt:
        print('Ctrl-C Detected, safely exitting')
        running = False


#Close out of our stuff nicely here
ser.close()
exit()


