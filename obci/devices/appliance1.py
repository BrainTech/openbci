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
        #assume that if first req is -1 the command is 'diodes on'
        #in the future middleware should allow to turn on selected field using -1 value
        if not len([i for i in d if i !=-1]):
            self.on()
            return

        clock  = 62500
        factor = float(p1) / float(p1 + p2)
        st = chr(3) # 'SSVEP_RUN'
 
        for i in range(len(d)):
            # i-th LED OFF
            if d[i] == 0:                       
                st += self.to_hex_word(0) + self.to_hex_word(255) 
            # i-th LED ON
            #below should work but doesnt - middleware doesnt have that feature
            elif d[i] == -1:
                st += self.to_hex_word(255) + self.to_hex_word(0)
            else:
                period = clock/d[i]
                bright = int((clock/d[i]) * factor)
                dark = period - bright
                st += self.to_hex_word(bright) + self.to_hex_word(dark)
 
        self.send(st)
 
    def blinkP300(self,d):
        clock  = 62500
        st = chr(4)
 
        for i in range(len(d)):
            period = int(clock*d[i]/1000.0)
            st += self.to_hex_word(period)
            print(period)
 
        self.send(st)

    def on(self):
        st = chr(2)
        self.send(st)

    def off(self):
        st = chr(1)
        self.send(st)
