# -*- coding: utf-8 -*-
## imports essential moduls 
import numpy as np
import matplotlib.pyplot as plt
import time, random, math
## As can be read: MULTIPLEXER
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

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
          
    
    
if __name__ == "__main__":
    NormalSessionAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
