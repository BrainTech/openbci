# -*- coding: utf-8 -*-
## imports moduls 
import numpy as np
import matplotlib.pyplot as plt
import time, random, math
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import samples_pb2

class NormalSessionAnalysis(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(NormalSessionAnalysis, self).__init__(addresses=addresses, type=peers.NORMAL_SESSION_ANALYSIS)
        #import all nessesery data
        importData()
        check()
        
    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_CATCHER_REQUEST_MESSAGE:
            self.send_message(message = cPickle.dumps(self.buffer[int(mxmsg.message)]), type = types.SIGNAL_CATCHER_RESPONSE_MESSAGE)
        elif mxmsg.type == types.FILTERED_SIGNAL_MESSAGE:
            self.add(mxmsg.message)
            self.no_response()
            
    def importData(self):
        """ THIS SHOULD IMPORT ALL NEEDED CONSTANTS!!!!!"""
        self.dataBank = samples_pb2.SampleVector()
        
        self.connection = connect_client(type = peers.NORMAL_SESSION_ANALYSIS)
        
        self.numOfLeds = int(self.connection.query(message = "NumOfFreq", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.sampingRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
       
       ## Time boundries
        self.floorTimeBoundry =  float(self.connection.query(message="FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.celingTimeBoundry = float(self.connection.query(message="CelingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.ledQueue = self.connection.query(message="............", type=types.DICT_GET_REQUEST_MESSAGE).message
        
        self.indexMap = self.numOfFreq * [0]
        
    
    def check(self):    
        """ Ask for data on every led flash and stores it """
        end = False
        dataBuffer =[]
        ledPanelBuffer = []
        
        while not end:
            
            ## Each time asks for sample and write down from witch led it was
            buffor += askForSamples()

            ## checks whenever it's time to stop
            if loopEnd():
                self.end = True
                
        
        ## Changes simple buffer list into matrix witch size are
        ## sampleRate x length of ledPanelBuffor list 
        self.buffer = np.array(buffer)
        self.buffer.reshape(len(self.ledQueue),self.sampingRate)
 
        self.analize()
    
    def askForSamples(self):
        """Asks for samples."""
        pass
    
    def loopEnd(self):
        """Checks if loop has ended"""
        pass
    
    
    def analize(self):
        """ Makes simples calculation over collected data. """
        ## Creates two matrices: 
        ## One is storing average values for each led, while the other
        ## is having average calculates from all samples without one led.
        self.averageForEachChannel = np.zeros( (self.numOfLeds,self.sampingRate),float)
        self.averageForAll = np.zeros( (self.numOfLeds,self.sampingRate),float)
        
        ## Creates matrices to calculate standard deviation
        self.differMatrix = np.zeros( (self.numOfLeds,self.sampingRate), float)
        self.standardDeviation = np.zeros( (1,self.sampingRate), float)
        
        ## For each build led...
        for led in range(self.numOfLeds):
            index = 0 
            
            # ... look through whole buffer ...
            for i in self.ledQueue:
                if i==led:
                    ## ... sieve and count data ... 
                    self.averageForEachChannel[led] +=buffer[i]
                
                    self.averageWithoutOne += buffer[i]
                    self.averageWithoutOne[led] -= buffer[i]
                    index += 1           
            # ... then calculate average.
            self.averageForEachChannel[led] /= index
        
        ## Calculate average for all:
        self.averageWithoutOne /= len(self.ledQueue)
        
        ## s = squareRoot( 1/N * sum( avrX - x)**2 )
        for led in range(self.numOfLeds):
            self.differMatrix[led] = self.averageForEachChannel[led] - self.averageWithoutOne
            self.standardDeviation += self.differMatrix[led]**2
        
        self.standardDeviation = (self.standardDeviation/self.numOfLeds)**(0.5)

        ## Counts how many standard deviation differ average value from each sample.
        ## Best match is led which vary the most from average result. 
        self.winner = 0
        for led in range(self.numOfLeds):
            temp = 0
            for val in self.differMatrix[self.floorTimeBoundry:self.celingTimeBoundry]:
                temp += val
            if (temp>self.winner):
                self.winner = led
        
        print "... And the winner is.... ", self.winner
        
        ## WINNER IS THE BEST MATCH


class TreningAnalysis(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(TreningAnalysis, self).__init__(addresses=addresses, type=peers.TRENING_ANALYSIS)
        
        #import all nessesery data
        self.importData()
        self.check()

    def handle_message(self, mxmsg):

        if mxmsg.type == DIODE_MESSAGE:
            t = variables_pb2.Blink()
            t.ParseFromString(mxmsg.message)
            self.timeOfLastHighlightDiod = t.timestamp             
            self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
            self.check()
                    
        self.no_response()
        
    def importData(self):
        self.connection = connect_client(type = peers.ANALYSIS)
        
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.sampleRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        ## HeighBar okresla pulap ktory ma zamalowac na wykresie diffNorm
        self.heighBar = float(self.connection.query(message="..............", type=types.DICT_GET_REQUEST_MESSAGE).message)
        ## czas calego odcinka ??
        self.seconds = 1
        ## list of diodes
        self.DiodSequence = (self.connection.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
        self.dataBank = samples_pb2.SampleVector()

        self.xLine = []
        self.diodQueuery = []
        self.index = 0
        
        # Things which will be needed
        self.good, self.bad = [], []
        self.nextBad, self.nextGood = (0,)*2
    
    def askForSamples(self):
      
        timeStamps = [] #self.seconds * self.sampleRate * [0] 
        wholeBuffer = np.zeros( (self.squares, self.seconds * self.sampleRate),float)
        buffer = []
        
        first = True
        for sample in dataBank.samples:
            if not first:
                wholeBuffer = np.column_stack((wholeBuffer,sample.value))
            else:
                wholeBuffer = np.array(sample.value)
                first = False
                
            timeStamps += [sample.timestamp]
             
        for i in range(len(timeStamps)):
            if self.timeOfLastHighlightDiod == timeStamps[i]:
                for j in range(self.sampleRate):
                    buffer.append(wholeBuffer[i+j])
        
        ################################
        actualDiod = None###############
        ################################
        
        return (buffer, actualDiod)
    
    def test(self, diod):
        "Test if presented character is THE CHOSEN ONE ! "
        self.diodQueuery += [diod]
        if diod==self.DiodSequence[self.index]:
            self.index += 1
            return True
        else: 
            self.index += 1
            return False
    
    def loopEnd(self):
        if len(self.diodQueuery) == len(self.DiodSequence):
            return True
        else:
            return False
    
    def check(self):    
        """ Ask for data on every led flash and stores it """

        buffer, present = askForSamples()
            
        if self.test(present):
            self.nextGood += 1
            self.good.append(buffer)
        else:
            self.nextBad += 1
            self.bad.append(buffer)
            
        if loopEnd():
            self.analize()
                
    def analize(self):
        """ Makes simples calculation over collected data. """
        ## Changes simple lists into arrays with data from each flash.
        ## Good are data collected when right diod was highLighted and bad
        ## are the rest.
        self.good = np.array(self.good)
        self.good.reshape(self.sampleRate,nextGood)
        
        self.bad = np.array(self.bad)
        self.bad.reshape(sampleRate,nextBad)
          
        
        ## Calculates averages values in the same time interval after flash
        self.avrGood = np.average(self.good,axis=0)
        self.avrBad  = np.average(self.bad, axis=0)
        
        ## Calculates correlation value
        ## r(x,y)**2 = (x|y) / ((x*y)**2)
        dotProduct = self.avrGood*self.avrBad
        goodNorm = ((self.avrGood**2).sum())**(.5)
        badNorm = ((self.avrBad**2).sum())**(.5)
        
        self.diffNorm = ( dotProduct / (goodNorm*badNorm) )**0.5     
    
    
    def plot(data):
        """ Creates plots from obtained data. """
        
        ## Looks for areas with r**2 higher than declared value.
        bar = False
        horBars = []
        for i in range(self.sampleRate):
            if (self.diffNorm[i]>heighBar):
                if not bar:
                    bar = True
                    horBars.append((i-1.)/self.sampleRate)
            if (diffNorm[i]<heighBar):
                if bar:
                    bar = False
                    horBars.append((i+1.)/self.sampleRate)
    
        
        # make a little extra space between the subplots
        plt.subplots_adjust(wspace=0.5)
        
        # sets time samples 
        dt = float(self.seconds)/self.sampleRate
        t = np.arange(0, self.seconds, dt)
         
        # plot with good, and bad
        plt.subplot(211)
        plt.plot(t, avrGood, 'b-', t, avrBad, 'g-')
        plt.xlim(0,self.seconds)
        plt.xlabel('time')
        plt.ylabel('average amplitude')
        plt.grid(True)
        
        if len(horBars):
            for bar in range(len(horBars)):
                if not bar%2:
                    plt.axvspan(horBars[bar], horBars[bar+1], fc = 'r', alpha = 0.3)
        
        ## Plot with difference
        plt.subplot(212)
        plt.xlim(0, seconds)
        plt.plot(t, diffNorm)
        plt.ylabel('difference in amplitude | really ??')
        plt.xlabel('time')
        
        if len(horBars):
            for bar in range(len(horBars)):
                print horBars[bar]
                if not bar%2:
                    plt.axvspan(horBars[bar],horBars[bar+1], fc = 'r', alpha = 0.3)
        def on_press(event):
            ###################################
            #### TUTAJ WYSYLA TO CO KLIKLES !!!
            ###################################
            self.xLine += [event.xdata]

        cid = plt.connect('button_press_event', on_press)
        plt.show()
    
class Selection:
    def __init__(self):
        self.sessionType = float(self.connection.query(message="SessionType", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
    def isTrening(self):
        if self.sessionType==1:
            return True
    
    def isNormalSession(self):
        if self.sessionType==2:
            return True
    
    def isTreningThenSession(self):
        if self.sessionType==3:
            return True
    
if __name__ == "__main__":
    selection = Selection()
    if selection.isTrening():
        TreningAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
    elif selection.isNormalSession():
        NormalSessionAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
    elif selection.isTreningThenSession():
        TreningAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
        NormalSessionAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
