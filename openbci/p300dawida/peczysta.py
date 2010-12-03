# -*- coding: utf-8 -*-
 
import numpy as np
import matplotlib.pyplot as plt
import time, random, math
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import samples_pb2
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

class Session(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(TreningAnalysis, self).__init__(addresses=addresses, type=peers.TRENING_ANALYSIS)
        
        #import all nessesery data
        self.importData()
        self.sessionTypeSelection()

    def handle_message(self, mxmsg):

        if mxmsg.type == DIODE_MESSAGE:
            t = variables_pb2.Blink()
            t.ParseFromString(mxmsg.message)
            self.timeOfLastHighlightDiod = t.timestamp             
            self.dataBank.ParseFromString(self.conn.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
            
            self.collectData()
                    
        self.no_response()

    def importData(self):
        ## Creates some constants
        self.seconds = 1
        self.diodeQueue = []
        self.index, self.bottomTime, self.topTime = [0]*3
        
        self.treningMode = False
        self.normalMode = False
                
        self.connection = connect_client(type = peers.ANALYSIS)
        self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.samplingRate = int(self.conn.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.diodeSequence = (self.conn.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
        
        
        self.dataBank = samples_pb2.SampleVector()

    def sessionTypeSelection(self):
        
        typeSelection = (self.conn.query(message="Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
            
        elif typeSelection=="TreningSession".lower():
            self.treningSession()
            
        elif typeSelection=="TreningAndNormal".lower():
            self.treningDataImport()

    def treningSession(self):
        ## HeighBar okresla pulap ktory ma zamalowac na wykresie diffNorm
        self.heighBar = float(self.conn.query(message="HeightBar", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.nextBad, self.nextGood = (0,)*2
        self.good, self.bad = [], []
        self.xLine = [0]*2  
        
        self.treningMode = True
         
    def normalSession(self):
        if not self.floorTimeBoundry:
            self.bottomTime = float(self.conn.query(message="FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        if not self.celingTimeBoundry:
            self.topTime = float( self.conn.query(message="CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message )
        
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
        
        for sample in dataBank.samples:
            wholeBuffer.append(sample.value)              
            timeStamps.append(sample.timestamp)
             
        timeStampPlace = timeStamsps.index(self.timeOfLastHighlightDiod)        
        for i in range(self.samplingRate):
            buffer.append(wholeBuffer[timeStampPlace+i])
        
        actualDiode = self.diodeSequence[self.index]
        
        data = (buffer, actualDiode)
        
        if self.treningMode:
            self.treningDataProcessor(data)
        elif self.normalMode:
            self.normalDataProcessor(data)
        else:
            raise Exception, 'message not handled'

    def treningDataProcessor(self, data):    
        """ Ask for data on every led flash and stores it """

        values, presentLed = data

        ## Checks if presentLed is associated with actual letter 
        if self.test(presentLed):
            self.nextGood += 1
            self.good = map(lambda x,y: x+y, self.good, values)
        else:
            self.nextBad += 1
            self.bad = map(lambda x,y: x+y, self.bad, values)
            
        ## checks whenever it's time to stop    
        if self.collectingEnd():
            self.treningAnalysis()

    def normalDataProcessor(self, data):    
        """ Ask for data on every led flash and stores it """
        
        values, presentLed = data
        
        ## Each time asks for sample and write down from witch led it was
        self.buffer[presentLed] += np.array(values)
        self.diodeCount[presentLed] += 1
        
        ## checks whenever it's time to stop
        if self.collectingEnd():
            self.normalAnalysis()

    def treningAnalysis(self):
        """ Makes simples calculation over collected data. """

        ## Calculates averages values in the same time interval after flash
        self.avrGood = np.array(self.good / self.good)        
        self.avrBad = np.array(self.bad/self.nextBad)
        
        ## Calculates correlation value
        ## r(x,y)**2 = (x|y) / ((x*y)**2)
        dotProduct = self.avrGood*self.avrBad
        goodNorm = ((self.avrGood**2).sum())**(.5)
        badNorm = ((self.avrBad**2).sum())**(.5)
        
        self.diffNorm = ( dotProduct / (goodNorm*badNorm) )**0.5     

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
        self.standardDeviation = np.zeros( (1,self.samplingRate), float)
        
        ## For each build led...
        for led in range(self.squares):
            self.averageForEachSquare[led] = self.buffer[led]/self.diodeCount[led]
         
        for led in range(self.squares):         
            self.averageWithoutOne[led] = np.sum(self.averageForEachSquare, 0) - self.averageForEachSquare[led]
            self.averageWithoutOne[led] /= (self.squares -1)
        
        ## s = squareRoot( 1/N * sum( avrX - x)**2 )
        for led in range(self.squares):
            self.differMatrix[led] = self.averageForEachSquare[led] - self.averageWithoutOne
            self.standardDeviation += self.differMatrix[led]**2
        
        self.standardDeviation = (self.standardDeviation/self.squares)**(0.5)

        ## Counts how many standard deviation differ average value from each sample.
        ## Best match is led which vary the most from average result. 
        self.winner = 0
        for led in range(self.squares):
            temp = 0
            for val in self.differMatrix[self.bottom:self.top]:
                temp += val
            if (temp>self.winner):
                self.winner = led
        
        print "... And the winner is.... ", self.winner
        self.conne.send_message(message = str(self.winner), type = types.DECISION_MESSAGE, flush=True)
        self.normalDataPlot()
        
        ## WINNER IS THE BEST MATCH
    
    def treningDataPlot(data):
        """ Creates plots from obtained data. """

        ## Looks for areas with r**2 higher than declared value.
        bar = False
        horBars = []
        for i in range(self.samplingRate):
            if (self.diffNorm[i]>self.heighBar):
                if not bar:
                    bar = True
                    horBars.append((i-1.)/self.samplingRate)
            if (self.diffNorm[i]<self.heighBar):
                if bar:
                    bar = False
                    horBars.append((i+1.)/self.samplingRate)
    
        
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
        
        if len(horBars):
            for bar in range(len(horBars)):
                if not bar%2:
                    plt.axvspan(horBars[bar], horBars[bar+1], fc = 'r', alpha = 0.3)
        
        ## Plot with difference
        plt.subplot(212)
        plt.xlim(0, self.seconds)
        plt.plot(t, self.diffNorm)
        plt.ylabel('difference in average amplitudes [r**2]')
        plt.xlabel('time [s]')
        
        if len(horBars):
            for bar in range(len(horBars)):
                print horBars[bar]
                if not bar%2:
                    plt.axvspan(horBars[bar],horBars[bar+1], fc = 'r', alpha = 0.3)

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
        "Checks whenever present diode is the right diode."
        if present==self.diodeSequence[self.index]:
            self.index += 1
            return True
        else:
            self.index += 1
            return False

    def collectingEnd(self):
        "Checks if that is the end of collecting data."
        if len(self.diodeQueue) == len(self.diodeSequence):
            return True
        else:
            return False
    
if __name__ == "__main__":
    Session(settings.MULTIPLEXER_ADDRESSES).loop()