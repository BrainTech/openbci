#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#



import serial, string
import os

# ser = serial.Serial('/dev/ttyUSB0', baudrate=9600)


# codes a decimal number a hexadecimally on two bytes 
def to_hex_word(a):
    #return chr(a / 256) + chr(a % 256)
    return chr(a%256) + chr(a/256)

# d = list of frequencies, p1:p2 = proportion time_diode_is_on/time_diod_is_off
# if you want diode number i to be OFF all the time send  d[i] = 0
# if you want diode number i to be ON all the time send  d[i] = -1
# in those two cases p1 and p2 do not matter


def blink_p300(i, p):
    
    st = chr(4) + chr(i) + chr(255) + chr(32) + chr(0) + chr(0)
    #ser.write(str)  
    print "blink_p300(" + str(i) + " " + str(p) + ")"
    

def blink(d, p1, p2):
    
    print "blink"
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
#    ser.write(str)
  
