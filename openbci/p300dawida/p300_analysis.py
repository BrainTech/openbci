#!/usr/bin/env python
# -*- coding: UTF-8 -*- 
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Dawid Laszuk <laszukdawid@gmail.com>

########################
# This module:
# Determines desired letter by classifying data.
########################
 
import numpy as np
import pylab as py
import time, os
import threading
import sys
#from os import popen

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import variables_pb2

from filtr import Filtr

## UWAGA! modul ten powinien byc uruchomiony chwile po uruchomieniu
## modulu wyswietlajacego bloczki. Potrzebne jest to do dobrego
## zaimportowania sekwencji wyswietlanej


class P300_bez:
    def __init__(self):

        self.connection = connect_client(type = peers.ANALYSIS)
                
        #import all nessesery data
        self.importData()
        self.sessionTypeSelection()
        
        os.system('rm checkAnalysis')
        
        ## Every XXX milisecons starts "action" function.
        self.timer = threading.Timer
        self.timer(0.1, self.preAction).start()
        
        
    def importData(self):
        """
        Imports necessary data from other sources
        """
        print "***** import data *****"
        
        ## Creates some constants
        self.index = 0
        
        self.treningMode = False
        self.normalMode = False        
        
        self.connection = connect_client(type = peers.ANALYSIS)

        
        self.samplingRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.SCbufferSize = int(self.connection.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.wholeBuffer = np.zeros(self.SCbufferSize)
        self.timeStamps = np.zeros(self.SCbufferSize)

        self.rowNum = int(self.connection.query(message = "P300Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.colNum = int(self.connection.query(message = "P300Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.squares = self.rowNum*self.colNum

        self.floorTimeBoundry = float(self.connection.query(message="P300FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.ceilingTimeBoundry = float( self.connection.query(message="P300CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message )

        
        self.dataBank = variables_pb2.SampleVector()

        self.repeat = int(self.connection.query(message = "P300Repeats", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.analysisTime = self.ceilingTimeBoundry - self.floorTimeBoundry      

        
        self.flag = ''
        self.num = 0
        self.timestamp = 0

        print "Please wait for the filter to fully load... "
        self.fn = 32.
        self.Fs = self.samplingRate
        self.filtr = Filtr(self.Fs,self.fn)
        print "OK!"
        
        
        self.dataVectorLength = np.ceil(self.analysisTime*self.fn)
        #~ self.buffer = np.zeros((self.squares, self.dataVectorLength), float)

        
    def getSequence(self):
        self.sequence = (self.connection.query(message="P300Sequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')
        #~ print "len(self.sequence): ", len(self.sequence)

    def getTreningSequence(self):
        
        self.treningChars = (self.connection.query(message="P300TrainingChars", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

        self.treningSequence = []
        textBank = np.load('textBank.npy')
        treningChars = np.array(self.treningChars)

        for i in treningChars:
            val = np.where(textBank==i)[0][0]
            r = val/self.colNum
            c = val%self.colNum
            self.treningSequence.append( str(r) + str(c) )

    def sessionTypeSelection(self):
        """
        Selects type of session based on bool values
        self.normalMode and self.treningMode.
        """

        typeSelection = (self.connection.query(message="P300Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
            
        elif typeSelection=="TreningSession".lower():
            self.treningSession()

        
    def preAction(self):
        """
        Seeks for flag in file, which tells if there was a blink.
        Repeats itself until true.
        """
        
        fName = 'checkAnalysis'

        # Checks whether there's a flag in file to
        # begin analysis.
        try:
            #~ self.t = time.time()
            checkAnalysis = open(fName)
            content = checkAnalysis.read(1)
            checkAnalysis.close()

            
            if content=='1':
                os.system('rm ' + fName)
                self.action()
            else:
                self.preAction()
                self.timer(0.05, self.preAction).start()
                
        except IOError:
            self.timer(0.05, self.preAction).start() 


    def action(self):
        """ 
        Creates a loop in which asks if there are any data to be taken.
        If there is anything sent by "diode_catcher" it starts computing.
        """

        tmp = (self.connection.query(message="P300Blink", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

        # data are sent as 'c0 timestamp'         
        self.flag = tmp[0][0]
        self.num = int(tmp[0][1])
        self.timestamp = float(tmp[1])
        
        print "{0:2}. {1}".format(self.index, tmp[0])
        
        self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
        
        self.collectData() 


    def treningSession(self):
        """
        Trening session. 
        """
        #~ print "***** trening session *****"
        self.getTreningSequence()
        self.getSequence()
        
        self.nextBad, self.nextGood = 0, 0
        self.n = 0

        length = self.dataVectorLength
        self.good = np.zeros( length )
        self.bad  = np.zeros( length )
        
        self.treningMode = True
         
    def normalSession(self):
        """
        Normal session. 
        """
        #~ print "***** normal session *****"
        self.getSequence()

        self.d = np.zeros((2,6))
        
        keys = self.__dict__.keys()
        if not 'self.w' in keys:
            try:
                self.w = np.load('w.npy')
            except IOError:
                info = "No file 'w' in this direction. Please start\n"
                info+= "trening session first."
                raise Exception, info

        if not 'self.c' in keys:
            try:
                self.c = np.load('c.npy')
            except IOError:
                info = "No file 'c' in this direction. Please start\n"
                info+= "trening session first."
                raise Exception, info        
        
        self.normalMode = True

        
    def collectData(self):
        """
        Sieve data from buffer and filters it.
        """

        buffer = []       # <- temporary buffer, just those needed
        n = 0
        for sample in self.dataBank.samples:
            self.wholeBuffer[n] = sample.value
            self.timeStamps[n] = sample.timestamp
            n +=1

        # BE AWARE! This loop goes backwards!
        # Searches for index of blink timestamp
        j=0 
        for i in range(1, self.SCbufferSize ):
            if self.timestamp + self.ceilingTimeBoundry > self.timeStamps[-i]:
                j=-i
                break

        if self.SCbufferSize +j -self.analysisTime*self.Fs >0:
            buffer = self.wholeBuffer[j-self.analysisTime*self.Fs:j:1]        
        
        if len(buffer):
            data = buffer
            #~ data = (data-data.mean())/data.var()
            data = self.filtr.filtr(data)
            data = data[::self.Fs/self.fn]

            self.index += 1 

            if self.treningMode:
                self.treningDataProcessor(data, self.num, self.flag)
            elif self.normalMode:
                self.normalDataProcessor(data, self.num, self.flag)
            else:
                raise Exception, 'message not handled'

        self.preAction()
            
    def treningDataProcessor(self, data, num, flag):    
        """
        Puts data into correct container. Waits until
        end of sequence to perform analysis.
        """

        blinkLine = flag, num
        
        ## Checks if presentLed is associated with actual letter 
        if self.test(blinkLine):
            self.good = np.vstack( (self.good, data) )
        else:
            self.bad = np.vstack( (self.bad, data) )

            
        ## checks whenever it's time to stop
        ## Stops after data from every letter is collected in trening word.
        if self.index >= len(self.sequence):
            self.n += 1
            self.index = 0
            if self.n == len(self.treningSequence):
                self.treningAnalysis()
        
    def treningAnalysis(self):
        """
        Calculates data for clasiffier.
        """
        #~ print "***** trening analysis *****"
        self.index = 0
        
        target = self.good
        nontarget = self.bad        
        
        ## Calculates averages values.
        ## First row is omitted, because they're 0.
        self.avrGood = target[1:].mean(axis=0)
        self.avrBad = nontarget[1:].mean(axis=0)

        meanDiff = self.avrGood - self.avrBad
        meanMean = 0.5*(self.avrGood + self.avrBad)

        # Covariance matrixes.
        # rowvar=0 means that columns are variable.
        goodCov = np.cov( target[1:], rowvar=0)
        badCov = np.cov( nontarget[1:], rowvar=0)

        # Inverting covariance matrix
        invertCovariance = np.linalg.inv( goodCov + badCov )

        # w - normal vector to separeting hyperplane
        # c - treshold for data projection
        w = np.dot( invertCovariance, meanDiff)
        c = np.dot(w, meanMean)
        
        ## Calculates correlation value
        ## r(x,y)**2 = (x|y) / ((x*y)**2)
        #~ dotProduct = self.avrGood*self.avrBad
        #~ goodNorm = ((self.avrGood**2).sum())**(.5)
        #~ badNorm = ((self.avrBad**2).sum())**(.5)
        
        #~ self.diffNorm = ( dotProduct / (goodNorm*badNorm) )**0.5

        print "We've done a research and it turned out that best values for you are: "
        print "w: ", w
        print "c: ", c
        np.save('w',w)
        np.save('c',c)
        
        #~ self.getSequence()
        #~ self.preAction()
            
    def normalDataProcessor(self, data, num, flag):    
        #~ """ Ask for data on every led flash and stores it. """
        #~ print "***** normal data processor *****"

        ## Puts data into correct container.
        #~ data = self.filtr.filtr(data)[::self.Fs/self.fn]
        d = np.dot(self.w, data) - self.c
        
        if flag=='c':
            self.d[0][num] += d
        elif flag=='r':
            self.d[1][num] += d
        
        ## checks whenever it's time to stop
        if self.index >= len(self.sequence):
            self.normalAnalysis()


    def normalAnalysis(self):
        """ Makes simples calculation over collected data. """
        #~ print "***** normal analysis *****"
        
        self.index = 0


        ## Average for rows and columns
        #~ self.avrCol = self.colArray.sum(axis=0)/self.colBlinkCount.sum()
        #~ self.avrRow = self.rowArray.sum(axis=0)/self.rowBlinkCount.sum()
        
        #~ self.avrForEachCol = self.colArray/self.colBlinkCount
        #~ self.avrForEachRow = self.rowArray/self.rowBlinkCount
        
        #~ self.avrColWithoutOne = np.zeros( (self.colNum, self.dataVectorLength), float)
        #~ self.avrRowWithoutOne = np.zeros( (self.rowNum, self.dataVectorLength), float)
        #~ self.colDiffer = np.zeros( (self.colNum, self.dataVectorLength), float)
        #~ self.rowDiffer = np.zeros( (self.rowNum, self.dataVectorLength), float)

        #for c in range(self.colNum):
            #if self.colBlinkCount[c]:
                #self.avrForEachCol[c] = self.colArray[c]/self.colBlinkCount[c]
        #for r in range(self.rowNum):
            #if self.rowBlinkCount[r]:
                #self.avrForEachRow[r] = self.rowArray[r]/self.rowBlinkCount[r]

        #for c in range(self.colNum):
            #self.avrColWithoutOne[c] = np.sum(self.avrForEachCol, 0) - self.avrForEachCol[c]
            #self.avrColWithoutOne[c] /= (self.colNum -1)
        #for r in range(self.rowNum):
            #self.avrRowWithoutOne[r] = np.sum(self.avrForEachRow, 0) - self.avrForEachRow[r]
            #self.avrRowWithoutOne[r] /= (self.rowNum -1)

        #for c in range(self.colNum):
            #self.colDiffer[c] = self.avrForEachCol[c] - self.avrColWithoutOne[c] 
        #for r in range(self.rowNum):
            #self.rowDiffer[r] = self.avrForEachRow[r] - self.avrRowWithoutOne[r]

        ## nie wiem dlaczego, ale zle srednie sa odejmowane
        #self.rowDiffer *= -1
        #self.colDiffer *= -1

        #floor = np.floor(self.floorTimeBoundry*self.samplingRate)
        #top = np.ceil(self.ceilingTimeBoundry*self.samplingRate)
        
        #print "floor: ", floor
        #print "top: ", top
        #winningRow = 0
        #sumRow = 0
        #print "rows: "
        #for r in range(self.rowNum):
            ##~ print self.rowDiffer[r][floor:top]
            #s = self.rowDiffer[r][floor:top].sum()
            #print str(r) + "  --  " + str(s)
            #if s > sumRow:
                #sumRow = s
                #winningRow = r

        c,r = 0,0
        dc, dr = self.d[0][0], self.d[1][0]
        for i in range(self.colNum):
            if self.d[0][i] > dc:
                c = i
                dc = self.d[0][i]
                
        for i in range(self.rowNum):
            if self.d[1][i] > dr:
                r = i
                dr = self.d[1][i]

        decision = str(c) + " " + str(r)
        print "And the winner is.... (col, row) : (%i, %i)" %(c+1, r+1)
        #self.conne.send_message(message = str(self.winner), type = types.DECISION_MESSAGE, flush=True)

        # winner = c*self.rowNum + r
        d = open('decision','w')
        d.write( decision )
        d.close()
        
        self.normalSession()
        #~ self.preAction()
       

    def test(self, present):
        """
        Checks whether column or row was highlit.
        """
        
        c, r = self.treningSequence[(self.index-1)/len(self.sequence)].strip().split()[0]
        flag, num = present

        if flag=='c':
            if num == int(c): return True
            else:             return False
        elif flag=='r':
            if num == int(r): return True
            else:             return False  
        elif flag=='K':
            print "%s: recived STOP command!" %sys.argv
            return True

if __name__ == "__main__":
    P300_bez()