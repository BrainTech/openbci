#!/usr/bin/env python
import time
import serial
import logging
import sys
import os


class SerialSender(object):
    def __init__(self, port_name):
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

    def close(self):
        self.port.close()
        
    def send(self, value):
        self.port.setRTS(value)


if __name__ == "__main__":

    dalej = True
    print "Podaj nazwe portu do otwarcia"
    while dalej:
        input = raw_input(">> ")
        try:
            s = SerialSender(input)
            dalej = False
        except serial.SerialException, e:
            print "Nieprawidlowa nazwa. Podaj prawidlowa nazwe portu do otwarcia:"
    
    s.open()
    print 'Wpisz:'
    print "'1' aby ustawic RTS na poziom logiczny 1"
    print "'0' aby ustawic RTS na poziom logiczny 0"
    print "'q' aby zakonczyc"
    input=1
    while 1 :
        input = raw_input(">> ")
        if input == '1':
            s.send(1)
            print "level 1"
        elif input == '0':
            s.send(0)
            print "level 0"
        elif input == 'q':
            s.close()
            exit()
