# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import socket
import pyautogui


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '10.0.0.147'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        pyautogui.press('playpause')
        exit