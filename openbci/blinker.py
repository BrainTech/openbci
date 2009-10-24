#!/usr/bin/env python
import serial
import os

ser = serial.Serial('/dev/ttyUSB0', baudrate=9600)


# codes a decimal number a hexadecimally on two bytes 
def to_hex_word(a):
    #return chr(a / 256) + chr(a % 256)
    return chr(a%256) + chr(a/256)

# d = list of frequencies, p1:p2 = proportion time_diode_is_on/time_diod_is_off
# if you want diode number i to be OFF all the time send  d[i] = 0
# if you want diode number i to be ON all the time send  d[i] = -1
# in those two cases p1 and p2 do not matter


def blink_p300(i, p):
    
    str = chr(4) + chr(i) + chr(255) + chr(32) + chr(0) + chr(0)
    ser.write(str)  
    

def blink(d, p1, p2):
    clock = 62500
    factor = float(p1) / float(p1 + p2)
    
    str = chr(3) #'R'
    for i in range(len(d)):
        # diode i OFF
        if d[i] == -1:                       
            str += to_hex_word(0) + to_hex_word(255) 
        # diode i ON
        elif d[i] == 0:
            #str += to_hex_word(255) + to_hex_word(0)
	    str = 'S'
        # diode i blinks d[i] times per second, p1:p2 = on_time:off_time in one blink
        else:
	    period = clock/d[i]
	    bright = int((clock/d[i]) * factor)
	    dark = period - bright
            str += to_hex_word(bright) + to_hex_word(dark)
    ser.write(str)
  
