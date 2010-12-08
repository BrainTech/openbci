#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import numpy as np
import matplotlib.pyplot as plt
import time, random, math, settings
import threading
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import variables_pb2
import sys
#===============================================================================
# What does variables do:
# self.blinkSequence -- sequence of blink index and timestamp (presently 8 pairs) 
# self.dataBank -- stores data from Google Protocol Buffer file
# self.squares -- quantity of squares to be displaied
# self.samplingRate -- how many samples do we take to analysis
# self.diodeSequence -- pregenerated list od diodes 
# self.bottomTime -- floor of P300 signal
# self.topTime -- ceiling of P300 signal
# self.xLine -- store top and bottom time boudries
# self.index -- counts how many times did diode flash
# self.dataVectorLength -- how many samples to consider for each blink.
#                          As a default blinkPeriod*samplingRate.
#
# self.blinks   -- liczba powtórzeń pojedynczych mrygnięć 
# self.seconds  -- czas przeznaczony na analize sygnalu (domyślnie 0.5 sekundy)
# self.blinkPeriod -- teoretycznie, czas między kolejnymi zapaleniami się diód
# self.SCbufferSize -- wielkość bufora przeznaczonego na dane
# self.mryg  -- liczba mrygniec do przeanalizowania
# self.repeatTime -- po tym czasie ponownie sie wlacza modul
#
# self.query -- adres dla blinkSequance, skad pobiera kolejne 8 indeksow diod
#
# self.trainingSequence  -- zestaw diod do ciwczenia
#
# self.treningMode -- if True, unlocks trening session
# self.normalMode -- if True, unlocks normal session
#===============================================================================


class P300:
    def __init__(self):
        print "***P300***__init__*****\n"
        self.connection = connect_client(type = peers.ANALYSIS)

        #import all nessesery data
        self.importData()
        self.sessionTypeSelection()
              
        self.timer = threading.Timer
        #self.timer(1, self.preAction).start()   
	self.channelNumber = 21
	self.firstBlinks = []
	self.collectTimestamps = []
    
    def start(self):
	self.timer(3, self.preAction).start()

    def preAction(self):
        #print "preAction"
        tmp = ""
        tmp = self.connection.query(message = "", type = types.DIODE_REQUEST, timeout = 15).message
        if len(tmp) == 0:
            self.timer(0.1, self.preAction ).start()
        else:
            self.query = tmp
            self.action()

    def action(self):
        """Tutaj sie dzieje magia... """
        
        # Initiats blinkSequence 
        #print "Action! "

        self.blinkSequence.ParseFromString(self.query)
        self.dataBank.ParseFromString(self.connection.query(message = str(self.channelNumber), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
 
        while ( ( (self.seconds + self.blinkSequence.blinks[7].timestamp) > self.dataBank.samples[-1].timestamp) and 
                (                 self.blinkSequence.blinks[0].timestamp  < self.dataBank.samples[0 ].timestamp)  ):
            self.dataBank.ParseFromString(self.connection.query(message = str(0), 
                                    type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, 
                                    timeout = 10).message)
        
        self.diodeSequence = (self.connection.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
        
        
        #print "\n\n*********ACTION****END*******\n\n"
        self.collectData() 



    def importData(self):
        ## Creates some constants
        ##print "\n*******IMPORT_DATA********\n\n"

        self.treningMode = False
        self.normalMode = False
        
        
        self.connection = connect_client(type = peers.ANALYSIS)

        self.diodeSequence = (self.connection.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.blinks = int(self.connection.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        


        self.samplingRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.blinkPeriod = float(self.connection.query(message="BlinkPeriod", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.SCbufferSize = int(self.connection.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)

        print "p300 ds ", self.diodeSequence
        self.trainingSequence = (self.connection.query(message="TrainingSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')

        
        self.dataBank = variables_pb2.SampleVector()

        self.mryg = 8
        self.dataVectorLength = self.blinkPeriod*self.samplingRate
        self.repeatTime = 1.0 # sec

        self.blinkSequence = variables_pb2.BlinkVector()
        
        
        self.seconds = self.blinkPeriod
        self.index, self.bottomTime, self.topTime = [0]*3        
        #print "\n*******IMPORT_DATA*****END*****\n\n"

    def sessionTypeSelection(self):
        #print "\n*******sessionTypeSelection*********\n\n"
        typeSelection = (self.connection.query(message="Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()

        elif typeSelection=="TreningSession".lower():
            self.treningSession()
           
        else:
            raise NameError('Session type name not matched. Please check hashtable.')
             

    def treningSession(self):
        ## HeighBar okresla pulap ktory ma zamalowac na wykresie diffNorm
        print "****TreningSession********\n\n"

        self.heighBar = float(self.connection.query(message="HeightBar", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.nextBad, self.nextGood = (0,)*2
        self.good = np.zeros( (1,self.dataVectorLength),float)
        self.bad  = np.zeros( (1,self.dataVectorLength),float)

        self.xLine = [0]*2  
        
        self.treningMode = True
         
    def normalSession(self):
        #if not self.floorTimeBoundry:
        print "***NORMAL*SESSION****"
        self.bottomTime = int(self.dataVectorLength*float(self.connection.query(message="FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message))
        self.topTime = int(self.dataVectorLength*float( self.connection.query(message="CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message ))
        
        self.buffer = np.zeros((self.squares, self.dataVectorLength), float)
        self.diodeCount = [0] * self.squares
        
        self.normalMode = True
        
    def collectData(self):
	self.collectTimestamps.append(time.time())
	self.firstBlinks.append(self.blinkSequence.blinks[0].timestamp)
	print "first blinks: ", self.firstBlinks
	print "collect times: ", self.collectTimestamps
	#print "FIRST BLINK: ", self.blinkSequence.blinks[0].timestamp
	OK = False
        "Sieve data from buffer"
        timeStamps = []   # <- list of whole timeStams
        wholeBuffer = []  # <- list of whole buffer received
        buffer = []       # <- temporary buffer, just those needed
        listOfDiodes = [] # <- list of diode indexes that blinked
       
        print "*****collectionData********\n\n"
	while (not OK):
        	self.dataBank.ParseFromString(self.connection.query(message = str(self.channelNumber), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
        
        	for sample in self.dataBank.samples:
            		wholeBuffer.append(sample.value)              
            		timeStamps.append(sample.timestamp)
            
        	#print "dlugosc wholeBuffer: " +str( len(wholeBuffer) )

        	## Scans list of timeStamps for the moment JUST before
        	## the blink event
        	ind = 0
        	while(ind < self.SCbufferSize) and (self.blinkSequence.blinks[7].timestamp > timeStamps[ind]):
            		ind = ind + 1
            	#print "TEST czy koniec sie miesci ",ind < self.SCbufferSize 
        	if (ind > self.SCbufferSize):
			OK  = False
        	else:
			OK = True
        	ind = 0
        	while (ind < self.SCbufferSize) and (self.blinkSequence.blinks[0].timestamp >= timeStamps[ind]):
            		ind = ind + 1
            	#print "TEST czy poczatek sie miesci ", ind < self.SCbufferSize
        	if (ind > self.SCbufferSize):
			OK = False
		else:
			if ind == 0:
				print "data[0] ", timeStamps[0]
				sys.exit(0) 
        
        # Tu dodaje przemnozenie przez blinkPeriod
        end = int(self.samplingRate*self.mryg*self.blinkPeriod)
        buffer = wholeBuffer[ind: ind+end]
#        for i in range(int(self.samplingRate*self.mryg*self.blinkPeriod)):
#            buffer.append(wholeBuffer[ind+i])      


        data = np.zeros( (self.mryg,self.dataVectorLength),float)
        for i in range(self.mryg):
            data[i] = buffer[int(i*self.dataVectorLength): int((i+1)*self.dataVectorLength)]
        
        for blink in self.blinkSequence.blinks:
            listOfDiodes.append(blink.index)

        #print "*****collectionData***END*****\n\n"
        
        if self.treningMode:
            self.treningDataProcessor(data)
        elif self.normalMode:            
            self.index += self.mryg
            self.normalDataProcessor(data, listOfDiodes)
        else:
            raise Exception, 'message not handled'

    def treningDataProcessor(self, valuesMatrix):    
        """ Ask for data on every led flash and stores it """
        #print "****treningDataProcessor*******\n\n"
        
        ## Checks if presentLed is associated with actual letter 
        for i in range(self.mryg):
            presentLed = self.diodeSequence[self.index]
            if self.test(self.diodeSequence[self.index]):
                self.nextGood += 1
                self.good = self.good + valuesMatrix[i]
                    
            else:
                self.nextBad += 1
                self.bad = self.bad + valuesMatrix[i]
                    
            ## checks whenever it's time to stop    
            if self.collectingEnd():
                self.treningAnalysis()
        
        self.preAction()

    def normalDataProcessor(self, data, listOfDiodes):    
        """ Ask for data on every led flash and stores it """
        #print "\n\n******normalDataProcessor******\n\n"
        
        for i in range(self.mryg):

            presentDiode = listOfDiodes[i]
            ## Each time asks for sample and write down from witch led it was

            self.buffer[presentDiode] += np.array(data[i])
            self.diodeCount[presentDiode] += 1

         
        ## checks whenever it's time to stop
        if self.collectingEnd():
            #print "normalDataProcessor -> normalAnalysis()   // koniec danych"
            self.normalAnalysis()

        ## if it's not over with collecting - start again
        self.preAction()


    def treningAnalysis(self):
        """ Makes simples calculation over collected data. """
        #print "\n****TRENING***ANALYSIS****\n\n"
        ## Calculates averages values in the same time interval after flash
        
        self.avrGood = np.array(self.good) / self.nextGood        
        self.avrBad = np.array(self.bad) /self.nextBad
        #print "self.good: ", self.good
        print "self.bad: ", self.bad
        print "self.avrGood: ", self.avrGood
        print "self.avrBad: ", self.avrBad

        ## Calculates correlation value
        ## r(x,y)**2 = (x|y) / ((x*y)**2)

        dotProduct = self.avrGood * self.avrBad
        print "dotProduct: ", dotProduct 
        goodNorm = np.sqrt( (self.avrGood**2).sum() )
        badNorm = np.sqrt( (self.avrBad**2).sum() )
        print "goodNorm ", goodNorm
        print "badNorm ", badNorm

        self.diffNorm = np.sqrt( dotProduct**2 / (goodNorm*badNorm) )

        print "trening: diffNorm: ", self.diffNorm
        print "\n****TRENING***ANALYSIS****END***\n\n"
    
        self.timer(self.repeatTime, self.restart).start()
  
    def normalAnalysis(self):
        """ Makes simples calculation over collected data. """
        #print "\n****NormalAnalysis*******\n\n"
        
        ## Creates two matrices: 
        ## One is storing average values for each led, while the other
        ## is having average calculates from all samples without one led.
        self.averageForEachSquare = np.zeros( (self.squares,self.dataVectorLength),float)
        self.averageWithoutOne = np.zeros( (self.squares,self.dataVectorLength),float)
        
        ## Creates matrices to calculate standard deviation
        self.differMatrix = np.zeros( (self.squares,self.dataVectorLength), float)
        #self.standardDeviation = np.zeros( (1,self.samplingRate), float)
        
        ## For each build led...
        for led in range(self.squares):
            if self.diodeCount[led]!=0:
                self.averageForEachSquare[led] = self.buffer[led]/self.diodeCount[led]
         
        for led in range(self.squares):         
            self.averageWithoutOne[led]  = self.averageForEachSquare.sum() - self.averageForEachSquare[led]
            self.averageWithoutOne[led] /= (self.squares -1)
        
        ## formula: stdDiv = squareRoot( 1/N * sum( avrX - x)**2 )
        for led in range(self.squares):
            self.differMatrix[led] = self.averageForEachSquare[led] - self.averageWithoutOne[led]
            #self.standardDeviation += self.differMatrix[led]**2
        
        #self.standardDeviation = (self.standardDeviation/self.squares)**(0.5)


        ## This is not time, it's its position !!
        print "self.bottomTime: " +str(self.bottomTime)
        print "self.topTime: " +str(self.topTime)
        

        ##  Wybor zwyciezcy
        self.winner = 0
        winValue = 0
        for led in range(self.squares):
            temp = 0
            for val in self.differMatrix[led][self.bottomTime:self.topTime]:
                temp += val**2
            print "led: " + str(led) + "  wartosc: " +str(temp)
            if (temp>winValue):
                self.winner = led
                winValue = temp

        tekst = ""
        f = open("diff.txt","w")
        for i in range(self.squares):
            tekst += "Macierz nr: " + str(i) + "\n"
            tekst += str(self.differMatrix[i]) + "\n\n"
        f.write(tekst)
        f.close()
        
        print "... And the winner is.... ", self.winner
        dec = variables_pb2.Decision()
        dec.type = 1
        dec.decision = self.winner


        #print "\n****NormalAnalysis*******\n\n"
            
        self.connection.send_message(message = dec.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)

        #self.connection.send_message(message = str(self.winner), type = types.DECISION_MESSAGE, flush=True)
        
        
        #self.timer(self.repeatTime, self.preAction).start()
        
        ## WINNER IS THE BEST MATCH
    
            
    def test(self, present):
        """Checks if the diode which blinked now is the one at which the user is supposed to look """
        #if present==self.diodeSequence[self.index]:
        print "index ", self.index, " blinks ", self.blinks, " squares ", self.squares, " iloczyn ", (self.index / (self.blinks * self.squares))
        print "trainingSeq ", self.trainingSequence[self.index / (self.blinks * self.squares)]
        print "present: ", present
        if present == 0:
            print "pres = 0"
        if int(present) == int(self.trainingSequence[self.index / (self.blinks * self.squares)]):
            print "true"
            self.index += 1
            return True
        else:
            self.index += 1
            return False

    def collectingEnd(self):
        "Checks if that is the end of collecting data."
        
        print "end: self.index: %4i len(diodeSequence): %i" %(self.index, len(self.diodeSequence) )
        
        if (self.index >= len(self.diodeSequence)):
            print " TRUE - (self.index >= len(self.diodeSequence)) " 
            return True

        else:
            print " FALSE - (self.index >= len(self.diodeSequence)) " 
            return False
    
    def restart(self):
        self.index = 0
        
        self.importData()
        self.preAction()
        
if __name__ == "__main__":
    P300().start()

