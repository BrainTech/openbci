#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import numpy as np
import matplotlib.pyplot as plt
import time, random, math, settings
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import variables_pb2

#===============================================================================
# What does variables do:
# self.dataBank -- stores data from Google Protocol Buffer file
# self.squares -- quantity of displaied squares
# self.samplingRate -- how many samples do we take to analysis
# self.diodeQueue -- list of highlit leds till now
# self.diodeSequence -- pregenerated list od diodes 
# self.bottomTime -- floor of P300 signal
# self.topTime -- ceiling of P300 signal
# self.xLine -- store top and bottom time boudries
# self.index -- counts how many times did diode flash
#
# self.treningMode -- if True, unlocks trening session
# self.normalMode -- if True, unlocks normal session
#===============================================================================

class P300:
    def __init__(self):
        self.connection = connect_client(type = peers.ANALYSIS)
        #import all nessesery data
        self.importData()
        self.sessionTypeSelection()
        self.st = 0

    def action(self):
        while True:
            self.lastBlink = variables_pb2.Blink()
            tmp = ''
            while (len(tmp) == 0):
                tmp = self.connection.query(message = "", type = types.DIODE_REQUEST, timeout = 15).message

            self.lastBlink.ParseFromString(tmp)
            self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
 
            print "action"
            t = self.dataBank.samples[len(self.dataBank.samples) - self.samplingRate - 1].timestamp
            #for x in self.dataBank.samples:
            #    print "tstamp ",x.timestamp
            while (t < self.lastBlink.timestamp):
                #time.sleep(0.005)
                self.dataBank = variables_pb2.SampleVector()
                self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
                print "wzmacniacz: " + str(self.dataBank.samples[len(self.dataBank.samples) - self.samplingRate - 1].timestamp)
                print "dioda: " + str(self.lastBlink.timestamp)
                t = self.dataBank.samples[len(self.dataBank.samples) - self.samplingRate - 1].timestamp
            print "po action"
            self.collectData() 


    def importData(self):
        ## Creates some constants
        self.seconds = 1
        self.diodeQueue = []
        self.index, self.bottomTime, self.topTime = [0]*3
        
        self.treningMode = False
        self.normalMode = False
                
        self.connection = connect_client(type = peers.ANALYSIS)
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.blinks = int(self.connection.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        

        self.samplingRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.diodeSequence = (self.connection.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')

        print "p300 ds ", self.diodeSequence
        self.trainingSequence = (self.connection.query(message="TrainingSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

        
        self.dataBank = variables_pb2.SampleVector()

    def sessionTypeSelection(self):
        
        typeSelection = (self.connection.query(message="Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
            
        elif typeSelection=="TreningSession".lower():
            self.treningSession()
            
        elif typeSelection=="TreningAndNormal".lower():
            self.treningDataImport()

    def treningSession(self):
        ## HeighBar okresla pulap ktory ma zamalowac na wykresie diffNorm
        self.heighBar = float(self.connection.query(message="HeightBar", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.nextBad, self.nextGood = (0,)*2
        self.good, self.bad = self.samplingRate * [0], self.samplingRate * [0]
        self.xLine = [0]*2  
        
        self.treningMode = True
         
    def normalSession(self):
        #if not self.floorTimeBoundry:
        self.bottomTime = float(self.connection.query(message="FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        #if not self.celingTimeBoundry:
        self.topTime = float( self.connection.query(message="CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message )
        
        self.buffer = np.zeros((self.squares, self.samplingRate), float)
        self.diodeCount = [0] * self.squares
        
        self.normalMode = True
        
    def treningAndNormal(self):
        "Starts trening session after which runs normal session"
        # TODO: nie wiem jakie tutaj polaczenie ma byc
        self.treningSession()
        self.normalSession()
    
    def collectData(self):
        "Sieve data from buffer"
        timeStamps = []
        wholeBuffer = [] 
        buffer = []
       
        print "collect"
        #self.dataBank.ParseFromString(self.connection.query(message = str(21), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
        for sample in self.dataBank.samples:
            wholeBuffer.append(sample.value)              
            timeStamps.append(sample.timestamp)
          
        # timeStampPlace = timeStamps.index(self.timeOfLastHighlightDiod)        
        # te timestampy nie musza byc identyczne
        #ind = len(timeStamps) - 1
        ind = 0
	#print "ind " + str(ind)
	#print "tstamp " + str(timeStamps[ind]) + "blink " + str(self.lastBlink.timestamp)
        while (self.lastBlink.timestamp >= timeStamps[ind]):
	    # print "ind " + str(ind)
	    # print "tstamp " + str(timeStamps[ind]) + "blink " + str(self.lastBlink.timestamp)
            ind = ind + 1

        for i in range(self.samplingRate):
            buffer.append(wholeBuffer[ind+i])
        # actualDiode = self.diodeSequence[self.index]
        # to rozumiem ze dioda ktora jest wlasnie pokazywana zgodnie z treningowa sekwencja 
        # nie pamietam jak mialo byc - czym jest diodeSequence, teraz jest sekwencja mrugniec
        # sekwencja treningowa to TrainingSeqience i ja tu dodaje oddzielnie zeby nie napsuc
        # bo nie wiem czy sekwencji mrugniec nie uzywasz do czegos
        # dodaje tez pobieranie sekwencji treningowej
        #  poniewaz self.index zwiekszasz o 1 za kazdym mrugnieciem, to to nie jest dobry numer diody z sesji treningowej
        # to jest numer mrygniecia, a nie diody ktora jest obserwowa, wiec trzeba zrobic
        # self.index/ (self.blinks * self.squares)
        # self.blinks = liczba mrygniec per dioda dla kazdej poezycji z sesji treningowej
        # self.squares = liczba kwadratow

         
        # actualDiode = self.trainingSequence[self.index / (self.blinks * self.squares)]

    	# print "aktualnie", actualDiode
        # print "aktualnie ", self.lastBlink.index
        # data = (buffer, actualDiode)
        data = buffer
        
        if self.treningMode:
            self.treningDataProcessor(data)
        elif self.normalMode:
            self.normalDataProcessor(data)
        else:
            raise Exception, 'message not handled'

    def treningDataProcessor(self, data):    
        """ Ask for data on every led flash and stores it """

        # values, presentLed = data
        values = data
        presentLed = self.lastBlink.index
        ## Checks if presentLed is associated with actual letter 
        if self.test(presentLed):
            self.nextGood += 1
            self.good = map(lambda x,y: float(x) + float(y), self.good, values)
            
        else:
            self.nextBad += 1
            self.bad = map(lambda x,y: float(x)+float(y), self.bad, values)
            
        ## checks whenever it's time to stop    
        if self.collectingEnd():
            self.treningAnalysis()

    def normalDataProcessor(self, data):    
        """ Ask for data on every led flash and stores it """
        self.index += 1 
        values = data 
	presentLed = self.lastBlink.index
        
        ## Each time asks for sample and write down from witch led it was
        self.buffer[presentLed] += np.array(values)
        self.diodeCount[presentLed] += 1
        
        ## checks whenever it's time to stop
        if self.collectingEnd():
            self.normalAnalysis()

    def treningAnalysis(self):
        """ Makes simples calculation over collected data. """
        print "TRENING ANALYSIS"
        ## Calculates averages values in the same time interval after flash
        
        self.avrGood = np.array(self.good) / self.nextGood        
        self.avrBad = np.array(self.bad) /self.nextBad
        print "self.good: ", self.good
        print "self.bad: ", self.bad
        print "self.avrGood: ", self.avrGood
        print "self.avrBad: ", self.avrBad

        ## Calculates correlation value
        ## r(x,y)**2 = (x|y) / ((x*y)**2)

        dotProduct = self.avrGood * self.avrBad
        print "dotProduct: ", dotProduct 
        goodNorm = ((self.avrGood**2).sum())**(.5)
        badNorm = ((self.avrBad**2).sum())**(.5)
        print "goodNorm ", goodNorm
        print "badNorm ", badNorm

        #self.diffNorm = ( dotProduct / (goodNorm*badNorm) )**0.5    

        #print "trening: diffNorm: ", self.diffNorm

        self.treningDataPlot()                
  
    def normalAnalysis(self):
        """ Makes simples calculation over collected data. """
        
        ## Creates two matrices: 
        ## One is storing average values for each led, while the other
        ## is having average calculates from all samples without one led.
        self.averageForEachSquare = np.zeros( (self.squares,self.samplingRate),float)
        self.averageWithoutOne = np.zeros( (self.squares,self.samplingRate),float)
        
        ## Creates matrices to calculate standard deviation
        self.differMatrix = np.zeros( (self.squares,self.samplingRate), float)
        #self.standardDeviation = np.zeros( (1,self.samplingRate), float)
        
        ## For each build led...
        for led in range(self.squares):
            self.averageForEachSquare[led] = self.buffer[led]/self.diodeCount[led]
         
        for led in range(self.squares):         
            self.averageWithoutOne[led] = np.sum(self.averageForEachSquare, 0) - self.averageForEachSquare[led]
            self.averageWithoutOne[led] /= (self.squares -1)
        
        ## s = squareRoot( 1/N * sum( avrX - x)**2 )
        for led in range(self.squares):
            self.differMatrix[led] = self.averageForEachSquare[led] - self.averageWithoutOne
            #self.standardDeviation += self.differMatrix[led]**2
        
        #self.standardDeviation = (self.standardDeviation/self.squares)**(0.5)

        ## Counts how many standard deviation differ average value from each sample.
        ## Best match is led which vary the most from average result. 
        self.winner = 0
        for led in range(self.squares):
            temp = 0
            for val in self.differMatrix[self.bottomTime:self.topTime]:
                temp += val
            if (temp>self.winner):
                self.winner = led
        
        print "... And the winner is.... ", self.winner
	dec = variables_pb2.Decision()
	dec.type = 1
	dec.decision = self.winner
	
	self.connection.send_message(message = dec.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)

        #self.connection.send_message(message = str(self.winner), type = types.DECISION_MESSAGE, flush=True)
        #self.normalDataPlot()
        
        ## WINNER IS THE BEST MATCH
    
    def treningDataPlot(self):
        """ Creates plots from obtained data. """
        print "PLOT"
        ## Looks for areas with r**2 higher than declared value.
        bar = False
        horBars = []
        #for i in range(self.samplingRate):
        #    if (self.diffNorm[i]>self.heighBar):
        #        if not bar:
        #            bar = True
        #            horBars.append((i-1.)/self.samplingRate)
        #    if (self.diffNorm[i]<self.heighBar):
        #        if bar:
        #            bar = False
        #            horBars.append((i+1.)/self.samplingRate)
    
        
        # make a little extra space between the subplots
        plt.subplots_adjust(wspace=0.5)
        
        # sets time samples 
        dt = float(self.seconds)/self.samplingRate
        t = np.arange(0, self.seconds, dt)
         
        # plot with good, and bad
        plt.subplot(211)
        plt.plot(t, self.avrGood, 'b-', t, self.avrBad, 'g-')
        plt.xlim(0,self.seconds)
        plt.xlabel('time [s]')
        plt.ylabel('average amplitude')
        plt.grid(True)
        
        #if len(horBars):
        #    for bar in range(len(horBars)):
        #        if not bar%2:
        #            plt.axvspan(horBars[bar], horBars[bar+1], fc = 'r', alpha = 0.3)
        
        ## Plot with difference
        #plt.subplot(212)
        #plt.xlim(0, self.seconds)
        #print "t: "
        #print t
        #print " diffNorm "
        #print self.diffNorm
       
        #plt.plot(t, self.diffNorm)
        #print "t: "
        #print t
        #print " diffNorm "
        #print self.diffNorm
        #plt.ylabel('difference in average amplitudes [r**2]')
        #plt.xlabel('time [s]')
        
        #if len(horBars):
        #    for bar in range(len(horBars)):
        #        print horBars[bar]
        #        if not bar%2:
        #            plt.axvspan(horBars[bar],horBars[bar+1], fc = 'r', alpha = 0.3)

        cid = plt.connect('button_press_event', self.whenButtonPressed)
        plt.show()
    
    def whenButtonPressed(event):
        """Action when mouse button was clicked. Adds to list
        if it was left button or removes from list if it were
        right button."""

        if event.button=='1':
            
            self.xLine[0] = self.xLine[1]
            self.xLine[1] = event.xdata
            print "added: x=%f" %event.xdata
            
        elif event.button=='3':
            if self.xLine[0]< self.xLine[1]:
                self.bottomTime = self.xLine[0]
                self.topTime = self.xLine[1]
            else:
                self.topTime = self.xLine[1]
                self.bottomTime = self.xLine[0]
            info = "bottom: %f\ntop: %f" %(self.bottomTime,self.topTime)
            print info
                
    def normalDataPlot(self):
        """Plots data from normal session"""
        self.x = math.floor(self.squares / math.sqrt(self.squares) )
        self.y = math.ceil(self.squares/self.x)

        dt = self.seconds / self.samplingRate
        t = np.arange(0.0,self.seconds,dt)
        
        matrix = np.zeros((self.squares, self.samplingRate),float)

        plt.ion()
        
        for led in range(self.squares):
            plt.subplot(self.x, self.y, led+1)
            plt.xlim((0,self.seconds))
            
            plt.xlabel("time [s]")
            plt.ylabel("voltage [V]")
            
            plt.plot(t,self.averageForEachSquare[led],"r",t,self.differMatrix[led],"b")
            plt.draw()
        plt.ioff()
        plt.show()
            
    def test(self, present):
        "Checks if the diode which blinked now is the one at which the user is supposed to look "
        #if present==self.diodeSequence[self.index]:
        #print "index ", self.index, " blinks ", self.blinks, " squares ", self.squares, " iloczyn ", (self.index / (self.blinks * self.squares))
        #print "trainingSeq ", self.trainingSequence[self.index / (self.blinks * self.squares)]
        #print "present: ", present
        if present == 0:
            print "pres = 0"
        if int(present) == int(self.trainingSequence[self.index / (self.blinks * self.squares)]):
            print "costam"
        if int(present) == int(self.trainingSequence[self.index / (self.blinks * self.squares)]):
            print "true"
            self.index += 1
            return True
        else:
            self.index += 1
            return False

    def collectingEnd(self):
        "Checks if that is the end of collecting data."
        # if (self.index >= self.blinks * self.squares * len(self.trainingSequence)):
        print "end: self.index: " + str(self.index) + "len(diodeSequence): " + str(len(self.diodeSequence))
        if (self.index >= len(self.diodeSequence)):

            return True

        if len(self.diodeQueue) == len(self.diodeSequence):
            return True
        else:
            return False
    
if __name__ == "__main__":
    P300().action()    

