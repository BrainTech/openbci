# -*- coding: utf-8 -*-

import hid
import time
import thread
import pygame

VENDOR_ID = 0x057e
PRODUCT_ID = 0x0306

base = pygame.USEREVENT
WIIBOARD_BUTTON_PRESS = base + 1
WIIBOARD_BUTTON_RELEASE = base + 2
WIIBOARD_MASS = base + 3
WIIBOARD_CONNECTED = base + 4
WIIBOARD_DISCONNECTED = base + 5

BUTTON_DOWN_MASK = 8

BUF_OUT = 22
BUF_IN = 25

DATA_TYPE = '0x32'

class BoardEvent(object):

	def __init__(self, topLeft, topRight, bottomLeft, bottomRight, buttonPressed, buttonReleased):
		self.topLeft = topLeft
		self.topRight = topRight
		self.bottomLeft = bottomLeft
		self.bottomRight = bottomRight
		self.buttonPressed = buttonPressed
		self.buttonReleased = buttonReleased
		# is not the true weight value 
		self.totalWeight = topLeft + topRight + bottomLeft + bottomRight
		
class Wiiboard(object):

	def __init__(self):
		self.LED = False
		self.address = None
		self.buttonDown = False
		self.status = "Disconnected"
		self.calibrate = [0, 0, 0, 0]
		self.calibrateRequest = True
		self.lastEvent = BoardEvent(0,0,0,0,False,False) 
		
	def connect(self):
		# "Try connect to wii balance board.."
		try:
			self.board = hid.device(VENDOR_ID, PRODUCT_ID)
		except IOError:
			raise Exception("Error: Device not found! You have to pair wii balance board first!")
		self.status = "Connected"
		#"Connect to wii balance board"
		#"Initialize wii balance board..."
		self.board.write(self._zero_pad([0x16, 0x04, 0xa4, 0x00, 0xf0, 0x01, 0x55], BUF_OUT))
		self.board.write(self._zero_pad([0x16, 0x04, 0xa4, 0x00, 0xf0, 0x01, 0x55], BUF_OUT))
		#print self.board.read(BUF_IN)
		time.sleep(0.5) 
		self.board.write(self._zero_pad([0x16, 0x04, 0xa4, 0x00, 0xfb, 0x01, 0x00], BUF_OUT))
		#print self.board.read(BUF_IN)
		time.sleep(0.5)
		self.board.write(self._zero_pad([0x12, 0x04, 0x32], BUF_OUT))
		time.sleep(0.5)
		#print self.board.read(BUF_IN)
    
	def startThread(self):
		thread.start_new_thread(self._receivethread, ())
	
	def disconnect(self):
		if self.status == "Connected":
			self.status = "Disconnected"
			try:
				self.board.close()
			except:
				pass
			print "Wii balance board disconnected"
		else:
		    pass
			
	def _createBoardEvent(self, data):
		buttonBytes = data[0:2]
		bytes = data[2:]
		buttonPressed = False
		buttonReleased = False

		state = (int(hex(buttonBytes[0]), 16) << 8 ) | int(hex(buttonBytes[1]), 16)
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

		rawTR = (int(hex(bytes[0]), 16) << 8) + int(hex(bytes[1]), 16) - self.calibrate[0]
		rawBR = (int(hex(bytes[2]), 16) << 8) + int(hex(bytes[3]), 16) - self.calibrate[1]
		rawTL = (int(hex(bytes[4]), 16) << 8) + int(hex(bytes[5]), 16) - self.calibrate[2]
		rawBL = (int(hex(bytes[6]), 16) << 8) + int(hex(bytes[7]), 16) - self.calibrate[3]
		boardEvent = BoardEvent(rawTL,rawTR,rawBL,rawBR,buttonPressed,buttonReleased)
		return boardEvent
		
	def _parseCalibration(self, data):
		bytes = data[2:]
		rawTR = (int(hex(bytes[0]), 16) << 8) + int(hex(bytes[1]), 16)
		rawBR = (int(hex(bytes[2]), 16) << 8) + int(hex(bytes[3]), 16)
		rawTL = (int(hex(bytes[4]), 16) << 8) + int(hex(bytes[5]), 16)
		rawBL = (int(hex(bytes[6]), 16) << 8) + int(hex(bytes[7]), 16)
		return [rawTR, rawBR, rawTL, rawBL]
		
	# Thread that listens for incoming data	
	def _receivethread(self):
		while self.status == "Connected":
			data = self.board.read(BUF_IN)
			intype = hex(data[0])
			if (self.calibrateRequest == True and intype == DATA_TYPE):
				self.calibrate = self._parseCalibration(data[1:11])
				self.calibrateRequest = False
			elif intype == DATA_TYPE:
					self.lastEvent = self._createBoardEvent(data[1:11])
					pygame.event.post(pygame.event.Event(WIIBOARD_MASS, mass=self.lastEvent))
			else:
				pass
		pygame.event.post(pygame.event.Event(WIIBOARD_DISCONNECTED))
				
	def getEvent(self):
		return self.lastEvent
		
	def isConnected(self):
		if self.status == "Connected":
			return True
		else:
			return False
	
	def _zero_pad(self, s, length):
		return [(s[i] if i < len(s) else 0x00) for i in range(length)]
