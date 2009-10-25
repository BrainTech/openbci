#!/usr/bin/env python

import numpy, cPickle, os, time, sys, random, Image#, blinker
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client



class UGM(QtGui.QWidget):
   
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        timer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
        timer.start(100)
        self.setWindowTitle(self.tr("SSVEP Speller"))
        self.connection = connect_client(type = peers.MONITOR)
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.szer = int(self.connection.query(message = "FrameWidth", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.freqs = self.connection.query(message = "Freqs", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        self.freqs = self.freqs.split(" ")
        for i in range(len(self.freqs)):
            self.freqs[i] = int(self.freqs[i])
        
        self.screenH = int(self.connection.query(message = "ScreenH", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.screenW = int(self.connection.query(message = "ScreenW", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.statusBar = int(self.connection.query(message = "StatusBar", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.Rows = int(self.connection.query(message = "Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.Cols = int(self.connection.query(message = "Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.message = ""
        #self.start_blinking() 
    def squareWidth(self):
        return 10
    def squareHeight(self):
        return 768
    # (x,y) : left top corner of the square
    # w, h : width, height

    def drawSquare(self, painter, x, y, w, h):
        #colorTable = [0x000000, 0xCC6666]
        color = QtGui.QColor(0x000000)
        painter.fillRect(x + 1, y + 1, w - 2, h - 2, color)

        painter.setPen(color.light())
        painter.drawLine(x, y + h - 1, x, y)
        painter.drawLine(x, y, x + w - 1, y)

        painter.setPen(color.dark())
        painter.drawLine(x + 1, y + h - 1, x + w - 1, y + h - 1)
        painter.drawLine(x + w - 1, y + h - 1, x + w - 1, y + 1)

    def paintEvent(self, event):
        szer = self.szer    
        painter = QtGui.QPainter(self)
        painter.setBrush(QBrush(QColor(0, 220, 0)))
        painter.drawRect(event.rect())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Vertical frames
        for i in range(self.Cols + 1):
            #self.drawSquare(painter, 341 - szer/2, 256 - szer/2, szer, 768)
            self.drawSquare(painter, i * self.screenW/self.Cols - szer/2, self.statusBar, szer, self.screenH)

            #self.drawSquare(painter, 682 - szer/2, 256 - szer/2, 0, szer, 768)
      
        # Horizontal frames
        for i in range(self.Rows + 1):
            #self.drawSquare(painter, 341 - szer/2, 256 - szer/2, szer, self.screenH)
            self.drawSquare(painter, 0, i * self.screenH/self.Rows - szer/2 + self.statusBar, self.screenW, szer)



        painter.setPen(QtGui.QColor(70, 200, 33))
        painter.setFont(QtGui.QFont('Decorative', 15))
        self.message = self.connection.query(message = "Message", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 0.1).message
        self.panel = self.connection.query(message = "Panel", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 0.1).message
        #print "graphics: ", self.panel
        squares = self.panel.split('::')
        for i in range(len(squares)):
            squares[i] = squares[i].split('|')
            squares[i] = [x.strip() for x in squares[i]]
	painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(15, 15, self.message)	

        fsize = 80
        bigfsize = 120
        offset = 25
        bigoffset = 80
        off = 80
        painter.setFont(QtGui.QFont('Decorative', 25))
        #painter.drawText((2 * 341) + off, fsize + off, "backspace")
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.setFont(QtGui.QFont('Decorative', 20))
        for i in range(self.squares):
            if (len(squares[i][0]) > 0):
                #print QtCore.QString(squares[i][0])
                pic = QtGui.QImage(QtCore.QString(squares[i][0]))
                pic = pic.scaled(self.screenW/self.Cols - self.szer , self.screenH/self.Rows - self.szer)
                painter.drawImage((i%self.Cols) * self.screenW/self.Cols + self.szer/2, self.statusBar + self.screenH/self.Rows * (i/self.Cols) + self.szer/2, pic)
            if (len(squares[i][1]) > 0):
                painter.drawText(((i%self.Cols) * self.screenW/self.Cols) + bigoffset, self.statusBar + self.screenH/self.Rows * (i/self.Cols) + bigfsize + bigoffset, squares[i][1])

        

    def start_mryganie(self):
        on = True
        for i in range(self.squares):
            how = self.freqs[i]
            if how > 0 :
                mrygacz.mrygaj(i, how, on=on)
    
    def stop_mryganie(self, i):
        mrygacz.mrygaj(i, 0, on=False)
    
    def stop_mryganie(self):
        for i in range(self.squares):
            self.stop_blinking(i)       


    def start_blinking(self):
        on = True
	d = []
	#print "freqs"
	#print self.freqs
	
	
	
	[d.append(int(x)) for x in self.freqs]
	#print "d", d

	blinker.blink(d, 1, 1)
   
   
    def stop_blinking(self):
	d = self.squares * [0]
	blinker.blink(d, 1, 1)


    def koniec(self):
        sys.exit(1)


    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ugm = UGM()
    ugm.showFullScreen()
    sys.exit(app.exec_())