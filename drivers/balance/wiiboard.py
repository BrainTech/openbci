#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bluetooth
import sys
import thread
import time
import pygame

base = pygame.USEREVENT
WIIBOARD_BUTTON_PRESS = base + 1
WIIBOARD_BUTTON_RELEASE = base + 2
WIIBOARD_MASS = base + 3
WIIBOARD_CONNECTED = base + 4
WIIBOARD_DISCONNECTED = base + 5

CONTINUOUS_REPORTING = "04"

COMMAND_LIGHT = 11
COMMAND_REPORTING = 12
COMMAND_REQUEST_STATUS = 15
COMMAND_REGISTER = 16
COMMAND_READ_REGISTER = 17

#input is Wii device to host
INPUT_STATUS = 20
INPUT_READ_DATA = 21
EXTENSION_8BYTES = 32

BUTTON_DOWN_MASK = 8
TOP_RIGHT = 0
BOTTOM_RIGHT = 1
TOP_LEFT = 2
BOTTOM_LEFT = 3

BLUETOOTH_NAME = "Nintendo RVL-WBC-01"


class BoardEvent(object):
    def __init__(self, topLeft, topRight, bottomLeft,
             bottomRight, buttonPressed, buttonReleased):
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.buttonPressed = buttonPressed
        self.buttonReleased = buttonReleased
        #convenience value
        self.totalWeight = topLeft + topRight + bottomLeft + bottomRight

class Wiiboard(object):

    # Sockets and status
    receivesocket = None
    controlsocket = None

    def __init__(self):
        self.calibration = []
        self.calibrationRequested = False
        self.LED = False
        self.address = None
        self.buttonDown = False
        for i in xrange(3):
            self.calibration.append([])
            for j in xrange(4):
                self.calibration[i].append(10000)
        self.status = "Disconnected"
        self.lastEvent = BoardEvent(0,0,0,0,False,False)
        try:
            self.receivesocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
            self.controlsocket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        except ValueError:
            raise Exception("Error: Bluetooth not found")

    def isConnected(self):
        if self.status == "Connected":
            return True
        else:
            return False

    # Connect to the Wiiboard at bluetooth address <address>
    def connect(self, address):
        if address == None:
            raise Exception("Non existant address")
            return
        self.receivesocket.connect((address, 0x13))
        self.controlsocket.connect((address, 0x11))
        if self.receivesocket and self.controlsocket:
            # Connected to Wiiboard at address --> address
            self.status = "Connected"
            self.address = address
            thread.start_new_thread(self._receivethread, ())
            self._calibrate()
            useExt = ["00",COMMAND_REGISTER,"04","A4","00","40","00"]
            self._send(useExt)
            self._setReportingType()
            # it posible to --> pygame.event.post(pygame.event.Event(WIIBOARD_CONNECTED))
        else:
            raise Exception("Error: Could not connect to Wiiboard at address " + address)

    # Disconnect from the Wiiboard
    def disconnect(self):
        if self.status == "Connected":
            self.status = "Disconnecting"
            while self.status == "Disconnecting":
                self._wait(1)
        try:
            self.receivesocket.close()
            self.controlsocket.close()
        except:
            pass
        # WiiBoard disconnected

    # Try to discover a Wiiboard
    def discover(self):
        print "Press the red sync button on the board now"
        address = None
        bluetoothdevices = bluetooth.discover_devices(duration = 6, lookup_names = True)
        for bluetoothdevice in bluetoothdevices:
            if bluetoothdevice[1] == BLUETOOTH_NAME:
                address = bluetoothdevice[0]
                # Found Wiiboard at address --> address
        if address == None:
            raise Exception("Error: No Wiiboards discovered.")
        return address

    def createBoardEvent(self, bytes):
        buttonBytes = bytes[0:2]
        bytes = bytes[2:12]
        buttonPressed = False
        buttonReleased = False

        state = (int(buttonBytes[0].encode("hex"),16) << 8 ) | int(buttonBytes[1].encode("hex"),16)
        if state == BUTTON_DOWN_MASK:
            buttonPressed = True
            if not self.buttonDown:
                pygame.event.post(pygame.event.Event(WIIBOARD_BUTTON_PRESS))
                self.buttonDown = True
        if buttonPressed == False:
            if self.lastEvent.buttonPressed == True:
                buttonReleased = True
                self.buttonDown = False
                pygame.event.post(pygame.event.Event(WIIBOARD_BUTTON_RELEASE))

        rawTR = (int(bytes[0].encode("hex"),16) << 8 ) + int(bytes[1].encode("hex"),16)
        rawBR = (int(bytes[2].encode("hex"),16) << 8 ) + int(bytes[3].encode("hex"),16)
        rawTL = (int(bytes[4].encode("hex"),16) << 8 ) + int(bytes[5].encode("hex"),16)
        rawBL = (int(bytes[6].encode("hex"),16) << 8 ) + int(bytes[7].encode("hex"),16)

        topLeft = self._calcMass(rawTL, TOP_LEFT)
        topRight = self._calcMass(rawTR, TOP_RIGHT)
        bottomLeft = self._calcMass(rawBL, BOTTOM_LEFT)
        bottomRight = self._calcMass(rawBR, BOTTOM_RIGHT)
        boardEvent = BoardEvent(topLeft,topRight,bottomLeft,bottomRight,buttonPressed,buttonReleased)
        return boardEvent


    def _calcMass(self, raw, pos):
        val = 0.0
        # calibration[0] is calibration values for 0kg
        # calibration[1] is calibration values for 17kg
        # calibration[2] is calibration values for 34kg
        if raw < self.calibration[0][pos]:
            return val
        elif raw < self.calibration[1][pos]:
            val = 17 * ((raw - self.calibration[0][pos]) / float((self.calibration[1][pos] - self.calibration[0][pos])))
        elif raw > self.calibration[1][pos]:
            val = 17 + 17 * ((raw - self.calibration[1][pos]) / float((self.calibration[2][pos] - self.calibration[1][pos])))
        return val

    def getEvent(self):
        return self.lastEvent
        
    def getLED(self):
        return self.LED

    # Thread that listens for incoming data
    def _receivethread(self):
        while self.status == "Connected":
            if True:
                data = self.receivesocket.recv(25)
                intype = int(data.encode("hex")[2:4] )
                if intype == INPUT_STATUS:
                #TODO: Status input received. It just tells us battery life really
                    self._setReportingType()
                elif intype == INPUT_READ_DATA:
                    if self.calibrationRequested == True:
                        packetLength = (int(str(data[4]).encode("hex"),16)/16 + 1)
                        self._parseCalibrationResponse(data[7:(7+packetLength)])
                        if packetLength < 16:
                            self.calibrationRequested = False
                elif intype == EXTENSION_8BYTES:
                    self.lastEvent = self.createBoardEvent(data[2:12])
                    pygame.event.post(pygame.event.Event(WIIBOARD_MASS, mass=self.lastEvent))
                else:
                    print "ACK to data write received"
        self.status = "Disconnected"
        self.disconnect()
        pygame.event.post(pygame.event.Event(WIIBOARD_DISCONNECTED))

    def _parseCalibrationResponse(self, bytes):
        index = 0
        if len(bytes) == 16:
            for i in xrange(2):
                for j in xrange(4):
                    self.calibration[i][j] = (int(bytes[index].encode("hex"),16) << 8 ) + int(bytes[index+1].encode("hex"),16)
                    index += 2
        elif len(bytes) < 16:
            for i in xrange(4):
                self.calibration[2][i] = (int(bytes[index].encode("hex"),16) << 8 ) + int(bytes[index+1].encode("hex"),16)
                index += 2
        
    # Send <data> to the Wiiboard
    # <data> should be an array of strings, each string representing a single hex byte
    def _send(self,data):
        if self.status != "Connected":
            return
        data[0] = "52"
        senddata = ""
        for byte in data:
            byte = str(byte)
            senddata += byte.decode("hex")
        self.controlsocket.send(senddata)

    #Turns the power button LED on if light is True, off if False
    #The board must be connected in order to set the light
    def setLight(self, light):
        val = "00"
        if light == True:
            val = "10"
        message = ["00", COMMAND_LIGHT, val]
        self._send(message)
        self.LED = light

    def _calibrate(self):
        message = ["00", COMMAND_READ_REGISTER ,"04", "A4", "00", "24", "00", "18"]
        self._send(message)
        self.calibrationRequested = True

    def _setReportingType(self):
        bytearr = ["00", COMMAND_REPORTING, CONTINUOUS_REPORTING, EXTENSION_8BYTES]
        self._send(bytearr)

    # Wait <millis> milliseconds
    def _wait(self,millis):
        time.sleep(millis / 1000.0)




