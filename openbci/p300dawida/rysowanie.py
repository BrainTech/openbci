# -*- coding: utf-8 -*-
## imports essential moduls 
import numpy as np
import sys, os, math
import PyQt4

import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

## As can be read: MULTIPLEXER
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings


#import samples_pb2
import variables_pb2

class PlotingAnalysis(FigureCanvas):
    def __init__(self, data):
        FigureCanvas.__init__(self, Figure())
	self.x = 2 # nie wiadomo za bardoz co tu mialo byc 
        # Read data from data
        self.squares, self.samplingRate, self.diodSequence = data

        # Size of plot grid
        self.row = math.floor(self.squares / math.sqrt(self.squares) )
        self.col = math.ceil(self.squares/self.x)

        # Lenght of x_axis
        self.seconds = 1.0
        
        self.t = np.arange(0,self.seconds,self.seconds/self.samplingRate)
        
        # Empty containers for future data
        self.matrix = np.zeros((self.squares,self.samplingRate), float)
        self.count = [0] * self.squares
        
        for i in range(self.squares):
            self.ax = self.figure.add_subplot(self.col,self.row, i+1)
            self.ax.grid()
            self.ax.set_xlim( 0,self.seconds ) 
            self.ax.set_xlabel("time [s]")
            self.ax.set_ylabel("voltage [V]")
            self.ax.set_lod(False)
            
            self.draw()  
                
        self.show()
        
        
    def updatePlot(self, data):
        """ Updates current plots with received data. Data should be a sequence
        with number of wanted to change square as first value and as second should
        obtain sequence with values (samplingRate size)"""
        
        num, values = data

        self.ax = self.figure.add_subplot(self.col, self.row, num+1)
        self.ax.clear()
        self.ax.grid()
        
        value = np.array(value)
        self.count[num] += 1        
        
        self.matrix[num] = ((self.count[num]-1)*self.matrix[num] + data)/self.count[num]
        self.ax.plot(self.t, self.matrix[num])

        self.draw()
        self.ax_background = self.copy_from_bbox(self.ax.bbox)

    def resetData(self):
        "Clear plots"
        self.matrix = np.zeros((self.squares,self.samplingRate), float)
        self.count = [0] * self.squares
        
        for num in range(self.squares):
            self.ax = self.figure.add_subplot(self.col, self.row, num+1)
            self.ax.clear()

class PlotHandler(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(PlotHandler, self).__init__(addresses=addresses, type=peers.ANALYSIS)
        print "created plot handler" 
        self.importData()
        
        # Creats class resposible for plotting data
        app = PyQt4.QtGui.QApplication(sys.argv)
        self.plot = PlotingAnalysis(self.data)
        self.plot.show()
    
        sys.exit(app.exec_())

    def importData(self):
        ## Connects to hashtable for constants
        #self.connection = connect_client(type = peers.ANALYSIS)
        print "import data" 
        self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)        
        self.samplingRate = int(self.conn.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.diodeSequence = (self.conn.query(message="DiodSequence", type=types.DICT_GET_REQUEST_MESSAGE).message).split(',')
        
        self.data = self.squares, self.samplingRate, self.diodeSequence
        
        self.index = 0
        self.dataBank = variables_pb2.SampleVector()
    
    def drawPlot(self):
        " Sieve data and sends it to plotting class."
	print "drawPlot"
        timeStamps = []
        wholeBuffer = []
        buffer = []
        
        for sample in dataBank.samples:
            wholeBuffer.append(sample.value)              
            timeStamps.append(sample.timestamp)
             
        for i in range(len(timeStamps)):
            if self.diodeTime == timeStamps[i]:
                for j in range(self.sampleRate):
                    buffer.append(wholeBuffer[i+j])
                break
        
        data = self.diodeSequence[self.index], buffer
        self.index += 1
        self.plot.updatePlot(data)
         
    def handle_message(self, mxmsg):
	print "handle ", mxmsg.type
	
        if mxmsg.type == DIODE_MESSAGE:
	    print "DIODE MESSAGE"
            t = variables_pb2.Blink()
            t.ParseFromString(mxmsg.message)
            self.diodeTime = t.timestamp             
            self.dataBank.ParseFromString(self.conn.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
            print "self.dataBank ",  self.dataBank  
            self.drawPlot()
                    
        self.no_response()

if __name__ == "__main__":
    PlotHandler(settings.MULTIPLEXER_ADDRESSES).loop()
