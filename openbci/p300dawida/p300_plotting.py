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
# Modul ten:
# Wyrysowuje wykresy dla sesji treningowej jak i zywklej.
#
########################

import numpy as np
import matplotlib.pyplot as plt

import variables_pb2
import sys, os, time

from scipy.signal import filtfilt, butter, buttord, lfilter, ellipord, ellip

from PyQt4 import QtGui, QtCore


from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

from canvas import CorrelationCanvas, GoodBadCanvas, NormalCanvas
from filtr import Filtr

# Trening:
# good - green
# bad - blue

# Normal:
# red - this avr
# blue - whole avr without this


#############################################
############## MAIN WINDOW ##################
#############################################
class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.connection = connect_client(type = peers.ANALYSIS)

        
        ## MENU BAR with
        ## File button
        self.fileMenu = QtGui.QMenu('&Quit', self)
        self.fileMenu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.fileMenu)


        self.importData()
        self.sessionTypeSelection()


        os.system('rm checkPlot')
        
        ## Every XXX milisecons starts "action" function.
        self.timer = QtCore.QTimer(self)
        #QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.action)
        self.timer.singleShot(500, self.preAction)
      
    def importData(self):
        """
        Imports necessary data from other sources.
        """
        #~ print "***** import data *****"
        
        ## Creates some constants
        self.index, self.bottomTime, self.topTime = [0]*3
        
        self.treningMode = False
        self.normalMode = False
        
        
        self.connection = connect_client(type = peers.ANALYSIS)
        
        self.samplingRate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.SCbufferSize = int(self.connection.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)

        self.rowNum = int(self.connection.query(message = "P300Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.colNum = int(self.connection.query(message = "P300Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.squares = self.rowNum*self.colNum

        
        self.dataBank = variables_pb2.SampleVector()

        
        self.repeat = int(self.connection.query(message = "P300Repeats", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)

        self.analysisTime = float(self.connection.query(message = "P300AnalysisTime", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) # sekund
        self.dataVectorLength = self.analysisTime*self.samplingRate
        self.buffer = np.zeros((self.squares, self.dataVectorLength), float)
                
        self.filtr = Filtr(self.samplingRate)

        # Blink parameters
        self.flag = ''
        self.num = 0
        self.timestamp = 0

        

    def preAction(self):
        """
        Seeks for flag in file, which tells if there was a blink.
        Repeats itself until true.
        """
        
        #print "***** preAction *****"
        fName = 'checkPlot'
        try:
            checkPlot = open(fName)
            content = checkPlot.read(1)
            checkPlot.close()
            
            # content
            # 1 - new data
            # 2 - new data + new char (clear plots)
            
            if content=='1':
                os.system('rm ' + fName)
                self.action()
            elif content=='2':
                os.system('rm ' + fName)
                self.clearPlots()
                self.action()
            else:
                self.timer.singleShot(50, self.preAction)
        except IOError:
                self.timer.singleShot(50, self.preAction)
                
            
    def action(self):
        """ 
        Creates a loop in which asks if there are any data to be taken.
        If there is anything sent by "diode_catcher" it starts computing.
        """
        #~ print "action"
        tmp = (self.connection.query(message="P300Blink", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

        # data are sent as 'c0 timestamp'                 
        self.flag = tmp[0][0]
        self.num = int(tmp[0][1])
        self.timestamp = float(tmp[1])
        print "{0:2}. {1}".format(self.index, tmp[0])
        
        self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
        
        self.collectData() 

    def collectData(self):
        """
        Sieve data from buffer and filters it.
        """

        #~ buffer = []       # <- temporary buffer, just those needed
        n = 0
        wholeBuffer = np.zeros( self.SCbufferSize )
        timeStamps = np.zeros( self.SCbufferSize )
        for sample in self.dataBank.samples:
            wholeBuffer[n] = sample.value
            timeStamps[n] = sample.timestamp
            n +=1
        
        # BE AWARE! This loop goes backwards!
        # Searches for index of blink timestamp
        j=0   
        for i in range(1, self.SCbufferSize ):
            if self.timestamp + self.analysisTime > timeStamps[-i]:
                j=-i
                break

        buffer = []
        if self.SCbufferSize +j -self.dataVectorLength >0:
            buffer = wholeBuffer[j-self.dataVectorLength:j:1]

        if len(buffer):
            data = buffer
            #~ data = (data-data.mean())/data.var()
            data = self.filtr.filtr(data)
            #~ data = data[::Fs/self.fn]

            self.index += 1 

            if self.treningMode:
                self.treningAnalysis(data, self.num, self.flag)
            elif self.normalMode:
                self.normalAnalysis(data, self.num, self.flag)
            else:
                raise Exception, 'message not handled'

        self.preAction()
            

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
        
    def getSequence(self):
        self.sequence = (self.connection.query(message="P300Sequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

    def sessionTypeSelection(self):
        """
        Selects type of session based on bool values
        self.normalMode and self.treningMode.
        """
        #~ print "***** session type selection *****"
        
        typeSelection = (self.connection.query(message="P300Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        self.setWindowTitle(typeSelection)        
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
        elif typeSelection=="TreningSession".lower():
            self.treningSession()
        else:
            raise NameError('Session type name not matched. Please check hashtable.')


    def treningSession(self):
        """
        Trening session. 
        """
        #~ print "***** Trening Session ****"
        self.getTreningSequence()
        self.getSequence()

        self.xLine = [0]*2 
        self.xLine[0] = float(self.connection.query(message="P300FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.xLine[1] = float(self.connection.query(message="P300CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.nextBad, self.nextGood = (0,)*2
        self.good = np.zeros( self.dataVectorLength,float)
        self.bad  = np.zeros( self.dataVectorLength,float)
        
        self.mainWidget = QtGui.QWidget(self)
        vertLayout = QtGui.QVBoxLayout(self.mainWidget)

        ## Plot showing goodAverage and badAverage signals
        self.goodBadPlot = GoodBadCanvas(self.mainWidget, dpi=50)
        self.gbMouseEvent = self.goodBadPlot.mpl_connect('button_press_event', self.clickEvent)
        self.goodBadPlot.setTime( self.analysisTime ) 
        self.goodBadPlot.drawLines( self.xLine[0], self.xLine[1] )
        
        vertLayout.addWidget(self.goodBadPlot)
            
        ## Plot showing correlation between good and bad signals
        self.correlation = CorrelationCanvas(self.mainWidget, dpi=50)
        self.corMouseEvent = self.correlation.mpl_connect('button_press_event', self.clickEvent)        
        self.correlation.setTime( self.analysisTime ) 
        self.correlation.drawLines( self.xLine[0], self.xLine[1] )
        
        vertLayout.addWidget(self.correlation)

        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
    
        self.treningMode = True
    
    def clickEvent(self, event):
        """
        What happens when one clicks on GoodBadPlot.
        Currently: changes values of topTime and bottomTime.
        """
        
        self.xLine[0] = self.xLine[1]
        self.xLine[1] = event.xdata
        
        if self.xLine[0] < self.xLine[1]:
            low, high = self.xLine
        else:
            high, low = self.xLine
        

        self.goodBadPlot.drawLines( low, high)
        self.correlation.drawLines( low, high)
        
        print "zaznaczony zakres:  %.3f -- %.3f" %(low,high)
        

    def normalSession(self):
        """
        Normal session. Creates array of plots. Each plot
        corresponds to one rectangle on speller's grid.
        """
        print "****** normal session *****"
        
        self.getSequence()
        
        ## Making plots
        self.mainWidget = QtGui.QWidget(self)
        gridLayout = QtGui.QGridLayout(self.mainWidget)

        self.plotList_row = []
        self.plotList_col = []
        text = ""
        for r in range(1,self.rowNum+1):
            blockName = "self.plot_r" + str(r)
            self.plotList_row.append(blockName)
            title = r"r"+str(r)
            
            text += "%s = NormalCanvas(self.mainWidget, dpi=50)\n" %(blockName)
            text += "%s.setTime(%f)\n" %(blockName, self.analysisTime)
            text += "%s.setTitle('%s')\n" %(blockName, title)
            text += "gridLayout.addWidget(%s,%i,%i)\n" %(blockName,1,r)
            
        for c in range(1, self.colNum+1):
            blockName = "self.plot_c" + str(c)
            self.plotList_col.append(blockName)
            title = r"c"+str(c)
            
            text += "%s = NormalCanvas(self.mainWidget, dpi=50)\n" %(blockName)
            text += "%s.setTime(%f)\n" %(blockName, self.analysisTime)
            text += "%s.setTitle('%s')\n" %(blockName, title)
            text += "gridLayout.addWidget(%s,%i,%i)\n" %(blockName,2,c)
        
        exec(text)
        
        
        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
        
        # Creates arrays for data
        self.colArray = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.rowArray = np.zeros( (self.rowNum, self.dataVectorLength), float)
        self.colBlinkCount = np.zeros( (self.colNum, 1) )
        self.rowBlinkCount = np.zeros( (self.rowNum, 1) )        

        self.avrForEachCol = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.avrForEachRow = np.zeros( (self.rowNum, self.dataVectorLength), float)
        self.avrColWithoutOne = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.avrRowWithoutOne = np.zeros( (self.rowNum, self.dataVectorLength), float)

        self.normalMode = True
        
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

      
    def normalAnalysis(self, data, num, flag):    
        """
        Makes simples calculation over collected data.        
        """
        #~ print "***** normal analysis *****"

        
        if( self.index >= len(self.sequence)):
            self.index = 0
        
        
        #~ values = data
        #~ flag, num = blinkLine
        data = (data - data.mean())/data.var()
        ## puts data into right place
        if flag=='c':
            self.colArray[num] += np.array(data)
            self.colBlinkCount[num] += 1
        elif flag=='r':
            self.rowArray[num] += np.array(data)
            self.rowBlinkCount[num] += 1


        ## Average for rows and columns
        self.avrCol = self.colArray.sum(axis=0)/self.colBlinkCount.sum()
        self.avrRow = self.rowArray.sum(axis=0)/self.rowBlinkCount.sum()
        
        for c in range(self.colNum):
            if self.colBlinkCount[c]:
                self.avrForEachCol[c] = self.colArray[c]/self.colBlinkCount[c]
        for r in range(self.rowNum):
            if self.rowBlinkCount[r]:
                self.avrForEachRow[r] = self.rowArray[r]/self.rowBlinkCount[r]
        

        for c in range(self.colNum):
            self.avrColWithoutOne[c] = np.sum(self.avrForEachCol, 0) - self.avrForEachCol[c]
            self.avrColWithoutOne[c] /= (self.colNum -1)
        for r in range(self.rowNum):
            self.avrRowWithoutOne[r] = np.sum(self.avrForEachRow, 0) - self.avrForEachRow[r]
            self.avrRowWithoutOne[r] /= (self.rowNum -1)

                    
        if flag=='r': 
            name = "Row"
            plot = self.plotList_row[num]
        else:
            name = "Col"
            plot = self.plotList_col[num]

        command = ""
        command+= plot 
        command+= ".updateFigure(self.avrForEachRow[%i],\
                       self.avr%sWithoutOne[%i])\n"  %(num,name,num)

        exec(command)
        self.preAction()

    def normalPlotUpdate(self):
        """
        Plot data in normal session. Temporary not used.
        """
        
        command = ""
        for r in range(self.rowNum):
            command+= self.plotList_row[r] 
            command+=".updateFigure(self.avrForEachRow[%i],\
                       self.avrRowWithoutOne[%i])\n"  %(r, r)

        for c in range(self.colNum):
            command+= self.plotList_col[c] 
            command+=".updateFigure(self.avrForEachCol[%i],\
                       self.avrColWithoutOne[%i])\n"  %(c, c)

        exec(command)
        
        self.timer.singleShot(10, self.preAction) 

    def clearPlots(self):
        """
        Clear plots by emptying matrixes and vectors.
        """
         
        self.colArray = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.rowArray = np.zeros( (self.rowNum, self.dataVectorLength), float)
        self.colBlinkCount = np.zeros( (self.colNum, 1) )
        self.rowBlinkCount = np.zeros( (self.rowNum, 1) )        


        self.avrForEachCol = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.avrForEachRow = np.zeros( (self.rowNum, self.dataVectorLength), float)
        self.avrColWithoutOne = np.zeros( (self.colNum, self.dataVectorLength), float)
        self.avrRowWithoutOne = np.zeros( (self.rowNum, self.dataVectorLength), float)
        
        
    def treningAnalysis(self, data, num, flag):    
        """
        Makes simples calculation over collected data.
        """
        #~ print "****TRENING***ANALYSIS****"

        blinkLine = flag, num

        ## Checks if in highlit line was desirable char
        if self.test(blinkLine):
            self.nextGood += 1
            self.good += data
        else:
            self.nextBad += 1
            self.bad += data

        ## Calculates averages values in the same time interval after flash
        if(self.nextGood):
            self.avrGood = self.good / self.nextGood
        else:
            self.avrGood = self.good

        if(self.nextBad):
            self.avrBad = self.bad /self.nextBad
        else:
            self.avrBad = self.bad
            
        # WHY ?? - this suposed to be r^2
        dotProduct = self.avrGood * self.avrBad
        goodNorm = np.sqrt( (self.avrGood**2).sum() )
        badNorm = np.sqrt( (self.avrBad**2).sum() )

        #~ self.diffNorm = np.sqrt( dotProduct**2 / (goodNorm*badNorm) )
        self.diffNorm = np.abs(self.avrGood - self.avrBad)
        #~ self.avrBad = (self.avrBad - self.avrBad.mean())/self.avrBad.var()
        #~ self.avrGood = (self.avrGood - self.avrGood.mean())/self.avrGood.var()


        ## Every third highligh refreshes plots.
        if (self.index % 5)==1:
            self.goodBadPlot.drawGoodBad( self.avrGood, self.avrBad )
            self.correlation.drawCor( self.diffNorm )

        ## Start again...
        self.timer.singleShot(100, self.preAction)
        
        
    def test(self, present):
        """
        Checks whenever highligh line is the right one.
        """
        #~ print "***** test *****"
                
        if self.index >= len(self.sequence):
            self.index = 0
            
        c, r = self.treningSequence[(self.index-1)/len(self.sequence)]
        flag, num = present
        
        if flag=='c':
            if num == int(c): return True
            else:                return False
        elif flag=='r':
            if num == int(r): return True
            else:                return False  
        elif flag=='K':
            print "%s: recived STOP command!" %sys.argv
            return True


            
if __name__=="__main__":
    qApp = QtGui.QApplication(sys.argv)

    progName = os.path.basename(sys.argv[0])

    window = MainWindow()
    window.setWindowTitle("%s" % progName)
    window.show()
    sys.exit(qApp.exec_())

