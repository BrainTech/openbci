#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import logging
import sys
import os

class SerialSender(object):
    def __init__(self, port_name, init_value):
        self.send_value = init_value
        import serial
        try:
            self.port = serial.Serial(
                port=port_name,
                baudrate=9600,
                #parity=serial.PARITY_ODD,
                #stopbits=serial.STOPBITS_TWO,
                #bytesize=serial.SEVENBITS
                )
        except serial.SerialException, e:
            print "Nieprawidlowa nazwa portu."
            raise e
        self.close()
    
    def open(self):
        self.port.open()
        self.send(self.send_value)

    def close(self):
        self.port.close()
        
    def send(self, value):
        self.port.setRTS(value)
        
    def send_next(self):
        self.send_value = (self.send_value + 1) % 2
        self.send(self.send_value)


