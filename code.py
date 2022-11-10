# License : GPLv2.0
# copyright (c) 2021  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Adapted by: Quino Bosch (quiboco)

import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

import supervisor

import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from board import *
import pwmio
import asyncio
import wifi
import os
import socketpool
import user_settings



duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,

}

def translateLine(line):
    spanish=['~',':',"'",'+','[','\\','@','^','{','%','(','-','"','*','|',',','&','<','`','}','.','_','=',']','!','>',';','?','#','$',')','/']
    us=['ª','Ñ','´','¿','`','çç','"','&','^','%',')',"'",'¨','(','Ç',',','/',';','º','*','.','?','¡','+','!',':','ñ','_','·','$','=','-']
    res=''
    for char in line:
        if char in us:
            i=us.index(char)
            char=spanish[i]
        res+=char
    return res


def convertLine(line):
    newline = []
    # print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    # print(newline)
    return newline

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:5] == "PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif(line[0:3] == "LED"):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()

defaultDelay = 0
        
def runPayload(payload):
    global defaultDelay
    lines=payload.split('\n')
    previousLine = ""
    for line in lines:
        line = line.rstrip()
        line=translateLine(line)
        if(line[0:6] == "REPEAT"):
            for i in range(int(line[7:])):
                #repeat the last command
                parseLine(previousLine)
                time.sleep(float(defaultDelay)/1000)
        else:
            parseLine(line)
            previousLine = line
        time.sleep(float(defaultDelay)/1000)

def recvPayload(s):
    buf=bytearray(1024)
    s.settimeout(1)
    try:
        num=s.recv_into(buf,1024)
        payload=str(buf[:num], 'utf-8')
        runPayload(payload)
    except Exception as e:
        print(e)
    s.close()

def createServer(ip):
    pool=socketpool.SocketPool(wifi.radio)
    while 1:
        s=pool.socket()
        s.bind((str(wifi.radio.ipv4_address),user_settings.BACKDOOR_PORT))
        s.listen(1)
        client,aux=s.accept()
        recvPayload(client)
        s.close()
        
wifi.radio.connect(user_settings.SSID, user_settings.KEY)
ip=wifi.radio.ipv4_address
while not ip:
    time.sleep(5)
    wifi.radio.connect(user_settings.SSID, user_settings.KEY)
    ip=wifi.radio.ipv4_address
    
createServer(ip)