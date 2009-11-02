#!/usr/bin/env python
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
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#

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
	self.trainingSequence = self.connection.query(message = "TrainingSequence", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
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
        # self.start_blinking() 
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
        # painter.setBrush(QBrush(QColor(0, 220, 0)))
	#painter.setBrush(QBrush(QColor(255, 255, 255)))
	painter.setBrush(QtGui.QColor(0, 0, 0))

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



        # painter.setPen(QtGui.QColor(9, 249, 17))
	#painter.setPen(QtGui.QColor(255, 255, 255))

        painter.setFont(QtGui.QFont('Bold', 25, 50))
        self.message = self.connection.query(message = "Message", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 0.1).message
        self.modeMessage = self.connection.query(message = "BlinkingMode", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 0.1).message

        self.panel = self.connection.query(message = "Panel", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 0.1).message
        #print "graphics: ", self.panel
        squares = self.panel.split('::')
        for i in range(len(squares)):
            squares[i] = squares[i].split('|')
            squares[i] = [x.strip() for x in squares[i]]
    	#painter.setPen(QtGui.QColor(0, 0, 0))
	painter.setPen(QtGui.QColor(255, 255, 255))

        #painter.drawText(15, 40, self.message)
	painter.drawText(15, 40, self.trainingSequence)

	#painter.setFont(QtGui.QFont('e', 45))	
	painter.setFont(QtGui.QFont('Bold', 45))	

        painter.drawText(self.screenW - 250, 80, self.modeMessage)	

        fsize = 80
        bigfsize = 120
        offset = 25
        bigoffset = 80
        off = 80
        painter.setFont(QtGui.QFont('Bold', 45, 100))
        #painter.drawText((2 * 341) + off, fsize + off, "backspace")
        # painter.setPen(QtGui.QColor(0, 0, 0))
	#painter.setPen(QtGui.QColor(255, 255, 255))

        painter.setFont(QtGui.QFont('Decorative', 30))
	painter.setFont(QtGui.QFont('Bold', 75, 85))

        for i in range(self.squares):
            if (len(squares[i][0]) > 0):
                #print QtCore.QString(squares[i][0])
                pic = QtGui.QImage(QtCore.QString(squares[i][0]))
                pic = pic.scaled(self.screenW/self.Cols - self.szer , self.screenH/self.Rows - self.szer)
                painter.drawImage((i%self.Cols) * self.screenW/self.Cols + self.szer/2, self.statusBar + self.screenH/self.Rows * (i/self.Cols) + self.szer/2, pic)
            if (len(squares[i][1]) > 0):
                painter.drawText(((i%self.Cols) * self.screenW/self.Cols) + bigoffset, self.statusBar + self.screenH/self.Rows * (i/self.Cols) + bigfsize + bigoffset, squares[i][1])

        


    def koniec(self):
        sys.exit(1)


    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ugm = UGM()
    ugm.showFullScreen()
    sys.exit(app.exec_())
