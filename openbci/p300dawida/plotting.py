#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

import variables_pb2
import sys, os, random, math, settings, time
from PyQt4 import QtGui, QtCore

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

#############################################
################# CANVAS ####################
#############################################

class Canvas(FigureCanvas):
    def __init__(self, parent=None, dpi=100):
        self.width, self.height = (3,2)
        
        self.fig = Figure(figsize=(self.width, self.height), dpi=dpi)
        self.axes = self.fig.add_subplot(1, 1, 1)

        self.timeArray = np.linspace(0, 1, 128 )

        # Set on clearing axes on each init
        self.axes.hold(False)
        self.computeInitialFigure()

        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def computeInitialFigure(self):
        pass

#############################################

class CorrelationCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.time = 1
        self.xMin = self.xMax = 0

    def computeInitialFigure(self):
        self.cor = np.zeros( len(self.timeArray) )
        self.axes.plot(self.timeArray, self.cor, 'r')
    
    def updateFigure(self):
        self.axes.cla()
        self.axes.plot(self.timeArray, self.cor, 'r')
        self.axes.axvspan(self.xMin, self.xMax, color='y')
        self.draw()
    
    def setTime(self, t):
        self.time = t
    
    def drawLines(self, xMin, xMax):
        self.xMin = xMin
        self.xMax = xMax
        self.updateFigure()
        
    def drawCor(self, cor):
        self.cor = cor
        self.timeArray = np.linspace(0,self.time, num=len(cor))
        self.updateFigure()
        
        
##########################################

class GoodBadCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.time = 1
        self.xMin = self.xMax = 0

    def computeInitialFigure(self):
        self.good = np.zeros( len(self.timeArray ))
        self.bad = np.zeros( len(self.timeArray ))
        
        self.axes.plot(self.timeArray, self.good, 'g',
               self.timeArray, self.bad,  'b')
    
    def updateFigure(self):
        print "\n\nUPDATE!\n\n"
        self.axes.cla()
        self.axes.plot(self.timeArray, self.good, 'g-',
               self.timeArray, self.bad,  'b-')        
        self.axes.axvspan(self.xMin, self.xMax, color='y')
        self.draw()
    
    def setTime(self, t):
        self.time = t
        
    def drawLines(self, xMin, xMax):
        self.xMin = xMin
        self.xMax = xMax
        self.updateFigure()
        
    def drawGoodBad(self, good, bad):
        self.good = good
        self.bad = bad
        self.timeArray = np.linspace(0,self.time, num=len(good))
        self.updateFigure()        
##########################################

class NormalCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.time = 1
        
    def computeInitialFigure(self):
        yArray = np.zeros( len(self.timeArray ))
        self.axes.plot(self.timeArray, yArray, 'r')
        print "computeInitialFigure(self)"

    def updateFigure(self, avrWhole, avrWithoutOne):
        print "update figure"
        self.timeArray = np.linspace(0, self.time, num=len(avrWhole))
        self.axes.plot(self.timeArray, avrWhole, 'r', 
                       self.timeArray, avrWithoutOne, 'b')
        self.draw()
    def setTime(self, t):
        self.time = t
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
                
        
        ## Every XXX milisecons starts "action" function.
        self.timer = QtCore.QTimer(self)
        #QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self.action)
        self.timer.singleShot(2000, self.preAction)
      

    def preAction(self):
        tmp = ""
        tmp = self.connection.query(message = "", type = types.DIODE_REQUEST, timeout = 15).message
        if len(tmp) == 0:
            self.timer.singleShot(100, self.preAction)
        else:
            self.action(tmp)
            
    def action(self, tmp):
        """ Creates a loop in which asks if there are any data to be taken.
            If there is anything sent by "diode_catcher" it starts computing."""
        
        # Initiats blinkSequence 
        self.blinkSequence = variables_pb2.BlinkVector()
        self.blinkSequence.ParseFromString(tmp)
	print "blink seq ", len(self.blinkSequence.blinks)
	print "self.SCbufferSize ", self.SCbufferSize
        self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
	print " len(self.dataBank.samples) ", len(self.dataBank.samples)
        while ((len(self.dataBank.samples)< self.SCbufferSize) or (self.blinkSequence.blinks[7].timestamp > self.dataBank.samples[self.SCbufferSize - 1].timestamp) or 
               (self.blinkSequence.blinks[0].timestamp < self.dataBank.samples[0].timestamp)):              
            self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
           
        # Imports (hardware) signal data 
        if self.st==0:
            czas = 1./self.dataVectorLength
            while (  ((czas + self.blinkSequence.blinks[7].timestamp) > self.dataBank.samples[-1].timestamp) and 
                        (self.blinkSequence.blinks[0].timestamp < self.dataBank.samples[0].timestamp)):
                self.dataBank.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
                
            t = self.dataBank.samples[ len(self.dataBank.samples) - self.samplingRate - 1].timestamp
            self.st =1
                
        self.diodeSequence = (self.connection.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
         
        self.collectData() 


    def collectData(self):
        "Sieve data from buffer"
        timeStamps = []   # <- list of whole timeStams
        wholeBuffer = []  # <- list of whole buffer received
        buffer = []       # <- temporary buffer, just those needed
        listOfDiodes = [] # <- list of diode indexes that blinked
        
        for sample in self.dataBank.samples:
            wholeBuffer.append(sample.value)              
            timeStamps.append(sample.timestamp)
            

        ind = 0
        while (ind < self.SCbufferSize and self.blinkSequence.blinks[7].timestamp >= timeStamps[ind]):
            ind = ind + 1
        assert(ind < self.SCbufferSize)
        
        ind = 0
        while (ind < self.SCbufferSize and self.blinkSequence.blinks[0].timestamp <= timeStamps[ind]):
            ind = ind + 1
        assert(ind < self.SCbufferSize)
 
        ind = 0 
        for i in range(int(self.samplingRate*self.mryg*self.blinkPeriod)):
            buffer.append(wholeBuffer[ind+i])      

        data = np.zeros( (self.mryg,self.dataVectorLength),float)
        for i in range(self.mryg):
            data[i] = buffer[int(i*self.dataVectorLength): int((i+1)*self.dataVectorLength)]
        
        for blink in self.blinkSequence.blinks:
            listOfDiodes.append(blink.index)

        
        if self.treningMode:
            self.treningDataProcessor(data)
        elif self.normalMode:
            self.normalDataProcessor(data, listOfDiodes)
        else:
            raise Exception, 'message not handled'
                    
    def sessionTypeSelection(self):
        typeSelection = (self.connection.query(message="Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        self.setWindowTitle(typeSelection)        
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
        elif typeSelection=="TreningSession".lower():
            self.treningSession()
        else:
            raise NameError('Session type name not matched. Please check hashtable.')


    def treningSession(self):
        print "****TreningSession********\n\n"

        self.xLine = [0]*2 
        ## HeighBar okresla pulap ktory ma zamalowac na wykresie diffNorm
        self.heighBar = float(self.connection.query(message="HeightBar", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.xLine[0] = float(self.connection.query(message="FloorTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.xLine[1] = float(self.connection.query(message="CeilingTimeBoundry", type=types.DICT_GET_REQUEST_MESSAGE).message)
        
        self.nextBad, self.nextGood = (0,)*2
        self.good = np.zeros( self.dataVectorLength,float)
        self.bad  = np.zeros( self.dataVectorLength,float)

                
        self.mainWidget = QtGui.QWidget(self)
        vertLayout = QtGui.QVBoxLayout(self.mainWidget)

        ## Plot showing goodAverage and badAverage signals
        self.goodBadPlot = GoodBadCanvas(self.mainWidget, dpi=100)
        self.gbMouseEvent = self.goodBadPlot.mpl_connect('button_press_event', self.clickEvent)
        self.goodBadPlot.setTime( self.analysisTime ) 
        self.goodBadPlot.drawLines( self.xLine[0], self.xLine[1] )
        
        vertLayout.addWidget(self.goodBadPlot)
            
        ## Plot showing correlation between good and bad signals
        self.correlation = CorrelationCanvas(self.mainWidget, dpi=100)
        self.corMouseEvent = self.correlation.mpl_connect('button_press_event', self.clickEvent)        
        self.correlation.setTime( self.analysisTime ) 
        self.correlation.drawLines( self.xLine[0], self.xLine[1] )
        
        vertLayout.addWidget(self.correlation)

        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
    
        self.treningMode = True
    
    def clickEvent(self, event):
        
        
        self.xLine[0] = self.xLine[1]
        self.xLine[1] = event.xdata
        
        if self.xLine[0] < self.xLine[1]:
            self.goodBadPlot.drawLines( self.xLine[0], self.xLine[1])
            self.correlation.drawLines( self.xLine[0], self.xLine[1])
        else:
            self.goodBadPlot.drawLines( self.xLine[1], self.xLine[0])
            self.correlation.drawLines( self.xLine[1], self.xLine[0])
        

    def normalSession(self):
        ## Making plots
        self.mainWidget = QtGui.QWidget(self)


        gridLayout = QtGui.QGridLayout(self.mainWidget)
        rowNum = 2
        colNum = 4

        self.plotList = []
        text = ""
        for row in range(1,rowNum+1):
            for col in range(1,colNum+1):
                blockName = "self.plot" + str(row) + str(col)
                self.plotList.append(blockName)

                text += "%s = NormalCanvas(self.mainWidget, dpi=100)\n" %(blockName)
                text += "gridLayout.addWidget(%s,%i,%i)\n" %(blockName,row,col)
        
        exec(text)
        
        
        self.mainWidget.setFocus()
        self.setCentralWidget(self.mainWidget)
        
        self.normalMode = True
        
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()


    def importData(self):
        ## Creates some constants
        self.seconds = 1
        self.diodeQueue = []
        self.index, self.bottomTime, self.topTime = [0]*3
        
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
        self.st = 0        
        self.dataVectorLength = self.blinkPeriod*self.samplingRate
        self.buffer = np.zeros((self.squares, self.dataVectorLength), float)
        self.diodeCount = [0] * self.squares        

        self.analysisTime = 1 # sekund
        
    def normalDataProcessor(self, data, listOfDiodes):    
        """ Ask for data on every led flash and stores it """

        for i in range(self.mryg):
            presentDiode = listOfDiodes[i]

            self.buffer[presentDiode] += np.array(data[i])
            self.diodeCount[presentDiode] += 1
            
        self.normalAnalysis(data, listOfDiodes)
            
    def normalAnalysis(self, data, listOfDiodes):
        """ Makes simples calculation over collected data. """

        self.averageForEachSquare = np.zeros( (self.squares,self.dataVectorLength),float)
        self.averageWithoutOne = np.zeros( (self.squares,self.dataVectorLength),float)
        
        self.differMatrix = np.zeros( (self.squares,self.dataVectorLength), float)
        #self.standardDeviation = np.zeros( (1,self.samplingRate), float)
        
        ## For each build led...
        for led in range(self.squares):
            if self.diodeCount[led]!=0:
                self.averageForEachSquare[led] = self.buffer[led]/self.diodeCount[led]
         
        for led in range(self.squares):         
            self.averageWithoutOne[led] = self.averageForEachSquare.sum() - self.averageForEachSquare[led]
            self.averageWithoutOne[led] /= (self.squares -1)
        
        ## s = squareRoot( 1/N * sum( avrX - x)**2 )
        for led in range(self.squares):
            self.differMatrix[led] = self.averageForEachSquare[led] - self.averageWithoutOne[led]

        self.normalPlotUpdate()

        
    def normalPlotUpdate(self):
        for num in range(self.squares):
            command = ""
            command+= self.plotList[num] 
            command+=".updateFigure(self.averageForEachSquare[%i],\
                       self.averageWithoutOne[%i])"  %(num, num)
            exec(command)

        self.timer.singleShot(1000, self.preAction) 

        
    def treningDataProcessor(self, valuesMatrix):    
        """ Ask for data on every led flash and stores it """
        print "****treningDataProcessor*******\n\n"
        
        ## Checks if presentLed is associated with actual letter 
        for i in range(self.mryg):
            presentLed = self.diodeSequence[i]
            print "Obecnie dioda: " + str(presentLed)
                      
            if self.test(self.diodeSequence[i]):
                self.nextGood += 1
                self.good += valuesMatrix[i]
                    
            else:
                self.nextBad += 1
                self.bad += valuesMatrix[i]
        
        self.treningAnalysis()

    def treningAnalysis(self):
        """ Makes simples calculation over collected data. """
        print "\n****TRENING***ANALYSIS****\n\n"
        ## Calculates averages values in the same time interval after flash

        if(self.nextGood):
            self.avrGood = np.array(self.good) / self.nextGood        
        else:
            self.avrGood = self.good

        if(self.nextBad):
            self.avrBad = np.array(self.bad) /self.nextBad
        else:
            self.avrBad = self.bad
            

        dotProduct = self.avrGood * self.avrBad
        goodNorm = np.sqrt( (self.avrGood**2).sum() )
        badNorm = np.sqrt( (self.avrBad**2).sum() )


        self.diffNorm = np.sqrt( dotProduct**2 / (goodNorm*badNorm) )

        self.goodBadPlot.drawGoodBad( self.avrGood, self.avrBad )
        self.correlation.drawCor( self.diffNorm )
    
        ## Start again...
        self.timer.singleShot(1000, self.preAction)
    def test(self, present):
        """Checks if the diode which blinked now is the one at which the user is supposed to look """

        if int(present) == int(self.trainingSequence[self.index / (self.blinks * self.squares)]):
            self.index += 1
            return True 
        else:
            self.index += 1
            return False
            
if __name__=="__main__":
    qApp = QtGui.QApplication(sys.argv)

    progName = os.path.basename(sys.argv[0])

    window = MainWindow()
    window.setWindowTitle("%s" % progName)
    window.show()
    sys.exit(qApp.exec_())

