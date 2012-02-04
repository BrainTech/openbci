#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import serial
import logging
import sys
import os
 
 
class Blinker(object):
    def __init__(self, port_name):
        try:
            self.port = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False
                )
        except serial.SerialException, e:
            print "Nieprawidłowa nazwa portu lub port zajęty."
            raise e
        self.close()

    def to_hex_word(self, a):
        '''encodes a decimal number hexadecimally on two bytes'''
        return chr(a%256) + chr(a/256)
 
    def open(self):
        self.port.open()
 
    def close(self):
        self.port.close()
 
    def send(self, value):
        self.port.write(value)
 
    def blinkSSVEP(self,d, p1, p2):
        '''
        d = list of frequencies;
        p1:p2 = ratio LED_on_time/LED_off_time
        if you want i-th LED to be OFF all the time send  d[i] = 0
        if you want i-th LED to be ON all the time send  d[i] = -1
        in these two cases p1 and p2 do not matter
        '''
        clock  = 62500
        factor = float(p1) / float(p1 + p2)
 
        str = chr(3) # 'SSVEP_RUN'
 
        for i in range(len(d)):
            # i-th LED OFF
            if d[i] == 0:                       
                str += self.to_hex_word(0) + self.to_hex_word(255) 
            # i-th LED ON
            elif d[i] == -1:
                str += self.to_hex_word(255) + self.to_hex_word(0)
                #str = 'S'
                # i-th LED blinks d[i] times per second
                # p1:p2 = on_time:off_time in one blink
            else:
                period = clock/d[i]
                bright = int((clock/d[i]) * factor)
                dark = period - bright
                str += self.to_hex_word(bright) + self.to_hex_word(dark)
 
        self.send(str)
 
    def blinkP300(self,d):
        clock  = 62500
        str = chr(4)
 
        for i in range(len(d)):
            period = int(clock*d[i]/1000.0)
            str += self.to_hex_word(period)
            print(period)
 
        self.send(str)

    def on(self):
        str = chr(2)
        self.send(str)

    def off(self):
        str = chr(1)
        self.send(str)
