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

# TO DO:
# - pozbyć się zmiennej self.treningSequence
# - pozbyć się niektórych funkcji z wciskaniem klawiszy


########################
# Modul ten:
# Wyświetla macierz znaków. Podświetla linie co określony czas.
#
########################

from PyQt4 import QtGui, QtCore
import numpy as np
import sys
import time, random
from os import popen, system

# made widgets
from widgets import MenuBar, RectangleArea

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

import variables_pb2

from sequence_gen import SequenceCreater

###########################
## Main window

class Main(QtGui.QWidget):
        
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        #~ self.plik = open('janusz_test','w')
        self.connection = connect_client(type = peers.ANALYSIS)


        self.rowNum = int(self.connection.query(message = "P300Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.colNum = int(self.connection.query(message = "P300Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)

        self.window = QtGui.QMainWindow()

        #self.fileName = 'temp_file'
        #self.file = open(self.fileName,'w+')
        
        ## Window options
        self.setWindowTitle("P300")
        
        self.screenWidth =self.window.width()
        self.screenHeight = self.window.height()
        
        
        # Jakies funkcje
        self.defineConstants()
        self.sessionTypeSelection()
        
        fontColor = int(self.connection.query(message="P300FontColor", type=types.DICT_GET_REQUEST_MESSAGE).message, 16)
        bgColor = int(self.connection.query(message="P300BackgroundColor", type=types.DICT_GET_REQUEST_MESSAGE).message, 16)
        rectColor = int(self.connection.query(message="P300RectangleColor", type=types.DICT_GET_REQUEST_MESSAGE).message, 16)
        
        self.fontColor = fC = QtGui.QColor(fontColor)
        self.bgColor = bgC = QtGui.QColor(bgColor) # RGB
        self.rectColor = txC = QtGui.QColor(rectColor) 

        ## Rectangle atributes - not in use temporary
        self.pen = QtGui.QPen()
        self.pen.setColor( self.rectColor )
        self.pen.setWidth( self.penWidth )


        ## Defining grids
        mainLayout = QtGui.QVBoxLayout(self)
        
        gridLayout = QtGui.QGridLayout()
        gridLayout.setSpacing( self.spacing )
        
        
        ## List of pointer to widgets
        self.regularList = []
        self.highlitList = []


        ## Menubar
        self.menuBar = MenuBar(self)
        self.menuBar.setFixedHeight(self.menuHeight)       
        self.menuBar.setFontSize(self.menuFontSize)
        self.menuBar.setFontColor(fC)
        self.menuBar.show()
        
        
        self.letters = []
        
        for y in range(self.rowNum):
            
            ## This makes list in form of a matrix
            self.letters.append( list() )
            self.regularList.append( list() )
            self.highlitList.append( list() )
            
            
            for x in range(self.colNum):
                command = ""

                text = self.textBank[y*self.colNum + x]                
                self.letters[y].append(text)
                
                ## Rectangle with inverted colors
                higBlockName = "h__r" + str(y) + "_c" + str(x)
                command += "\n%s = RectangleArea(text, 'h', bgC, txC, self.rectSize )" %higBlockName
                command += "\nself.highlitList[y].append(%s)" %higBlockName
                command += "\ngridLayout.addWidget(%s, y, x, QtCore.Qt.AlignCenter)" %higBlockName
                                
                ## Rectangle with normal colors
                regBlockName = "r__r" + str(y) + "_c" + str(x)                
                command += "\n%s = RectangleArea(text, 'r', bgC, txC, self.rectSize )" %regBlockName              
                command += "\nself.regularList[y].append(%s)" %regBlockName
                command += "\ngridLayout.addWidget(%s, y, x, QtCore.Qt.AlignCenter)" %regBlockName
                command += "\n%s.show()" %regBlockName
                
                exec(command)

        
        ## Adding and setting layouts
        mainLayout.addWidget(self.menuBar)
        mainLayout.addLayout(gridLayout)
        self.setLayout(mainLayout)
        
        ## Color of background
        self.setStyleSheet("QWidget { background-color: %s }" % self.bgColor.name())
        
        ## Timer for blinking part
        self.timer = QtCore.QTimer()
        
    def __del__(self):
        """
        Destructor: removes files with flags.
        """
        #~ self.plik.close()
        system("rm " + self.checkAnalysisName)
        system("rm " + self.checkPlotName)
        system("rm textBank.npy")

    def defineConstants(self):
        """
        Defines constants values.
        """
        
        ## Some temporary flags
        self.playMode = False
        self.seqFinished = False

        self.treningMode = False
        self.normalMode = False
        
        # Filenames
        self.fileName = "p300_chars"
        self.decisionFile = "decision"
        self.checkPlotName = "checkPlot"
        self.checkAnalysisName = "checkAnalysis"

        ## 
        self.menuFontSize = int(self.connection.query(message="P300FontSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.SCbufferSize = int(self.connection.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
                
        self.blinkBuff_length = int(self.connection.query(message="P300BlinkBuff", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.blinkBuff = ['00 0']*self.blinkBuff_length
        self.penWidth = 3

        # Blink
        self.blinkTime = 1000*float(self.connection.query(message="P300BlinkTime", type=types.DICT_GET_REQUEST_MESSAGE).message)        
        self.blinkInterval = 1000*float(self.connection.query(message="P300BlinkBreak", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.blinkPeriod = self.blinkTime + self.blinkInterval  # ms
        


        self.repeat = int(self.connection.query(message = "P300Repeats", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.count = 0

        squareSize = float(self.connection.query(message="P300SquareSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.rectSize = (squareSize, squareSize)
        
        ## select language (?)
        # pol - Polish
        # eng - English
        # tmp - chwilowy
        self.language = "tmp"
        self.textBank = self.letterBank()

#        self.letterBank = self.letterBank.decode('UTF-8')
#        print "after: ", self.letterBank
        
        ## Offset values - not using temporary
        self.menuHeight = 1.7*self.menuFontSize
        self.topOffset = 0.1*self.screenHeight
        self.bottomOffset = 0.1*self.screenHeight
        self.leftOffset = 0.1*self.screenWidth
        self.rightOffset = 0.1*self.screenWidth
        self.spacing = 10

        
        ## Defining sequence list
        temp = self.rowNum, self.colNum, self.repeat
        self.sequence = SequenceCreater(temp[0], temp[1], temp[2]).returnSequence()
        
        self._set_hashtable_value( "P300Sequence", ' '.join(self.sequence) )

        
    def _set_hashtable_value(self, key, value):
        """
        Saves data into hashtable file.
        """
        
        l_var = variables_pb2.Variable()
        l_var.key = key
        l_var.value = value
        self.connection.send_message(message = l_var.SerializeToString(), 
                                     type = types.DICT_SET_MESSAGE, flush=True)
    def sessionTypeSelection(self):
        """
        Selects type of session.
        """
        
        typeSelection = (self.connection.query(message="P300Session", type=types.DICT_GET_REQUEST_MESSAGE).message).lower()
        self.setWindowTitle("P300 - " + typeSelection)        
        
        if typeSelection=="NormalSession".lower():
            self.normalSession()
        elif typeSelection=="TreningSession".lower():
            self.treningSession()
        else:
            raise NameError('Session type name not matched. Please check hashtable for typo.')

    def normalSession(self):
        self.normalMode = True
    
    def treningSession(self):
        self.treningMode = True
        self.treningChars = (self.connection.query(message="P300TrainingChars", type=types.DICT_GET_REQUEST_MESSAGE).message).split(' ')

        self.treningSequence = []
        textBank = np.array(self.textBank)
        treningChars = np.array(self.treningChars)

        for i in treningChars:
            val = np.where(textBank==i)[0][0]
            r = val/self.colNum
            c = val%self.colNum
            self.treningSequence.append( str(c) + str(r) )
        
        self.n = 0
        

    def letterBank(self):
        """
        Creates list of letters/symbols filling rectangles.
        """
        
        polishAlphabet = u'AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ' # len = 32
        latinAlphabet = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ' # len = 26
        funcWordEng = [u"DEL", u"SPACE", u"CLEAR"] # len = 3
        funcWordPol = [u"USUŃ", u"ODSTĘP", u"WYCZYŚĆ"] # len = 3
        numCharacters = u'0123456789' # len = 10
        characters = u'?,.!' # len = 5
        functionChars = [u'message', u'func_2', u'func_3', u'func_4'] # len = ?
        
        
        length = self.rowNum * self.colNum
        charList = []
        
        if self.language.lower() == "pol":
            
                for num in numCharacters:
                    charList.append(num)
            
                for char in polishAlphabet:
                    charList.append(char)
            
                for char in characters:
                    charList.append(char)
            
                for func in funcWordPol:
                    charList.append(func)
            
                if len(charList) < length:
                    charList.insert(-len(funcWordPol), u'message')
                    
                while(len(charList) < length ):
                    charList.insert(-len(funcWordPol),"func")
        
        elif self.language.lower() == "eng":
            while (len(charList) <= length ):
                for char in latinAlphabet:
                    charList.append(char)
                    
                for num in numCharacters:
                    charList.append(num)
                
                for char in characters:
                    charList.append(char)
                    
                if len(charList) < length:
                    charList.insert(-len(funcWordPol), u'message')
                    
                for func in funcWordEng:
                    charList.append(func)
                    
                while(len(charList) < length ):
                    charList.insert(-len(funcWordPol),"func")
        
        elif self.language.lower() == "tmp":
            while (len(charList) <= length ):
                for char in "ABCDEFGHIJKLMNOPRSTUWYZ":
                    charList.append(char)
                    
                for num in numCharacters:
                    charList.append(num)
                    
                for func in funcWordPol:
                    charList.append(func)

        np.save('textBank',np.array(charList))
        return charList
    
    def resizeEvent(self, event):
        """
        What is done, when window changes its size.
        """
        self.menuBar.update()
            
    def keyPressEvent(self, event):
        """
        After key is pressed.
        """
        
        if event.key() == QtCore.Qt.Key_Escape:
            # ESC to shut down program
            quit()  
            
        elif event.key() == QtCore.Qt.Key_Tab:
            # TAB - RANDOM HIGHLIGHT
            self.y = random.randint(0, self.rowNum-1)
            self.x = random.randint(0, self.colNum-1)
                        
            print "x: ", self.x, " y: ", self.y
            
            self.hideElement()            
            
        elif event.key() == QtCore.Qt.Key_P:
            # P - play = star sequence
            time.sleep(1.5)
            self.play()
            
        elif event.key() == QtCore.Qt.Key_R:
            # R - RANDOM
            self.y = random.randint(0, self.rowNum-1)
            self.x = random.randint(0, self.colNum-1)
            
            print "x: ", self.x, " y: ", self.y
            self.showElement()
            char = self.letters[self.y][self.x]
            if len(char)==1:
                self.menuBar.addLetter(char)
            elif char==u"SPACE" or char==u"ODSTĘP":
                self.menuBar.addLetter(" ")
            elif char==u"DEL" or char==u"USUŃ":
                self.menuBar.delLetter()
            elif char==u"CLEAR" or char==u"WYCZYŚĆ":
                self.menuBar.clearText()
            
        
        elif event.key() == QtCore.Qt.Key_D:
            #  D -DEL
            self.menuBar.delLetter()
        
        elif event.key() == QtCore.Qt.Key_C:
            #  C - CLEAR
            self.menuBar.clearText()        
        
        elif event.key() == QtCore.Qt.Key_S:
            #  S - SPACE
            self.menuBar.addLetter(" ")
            
        elif event.key() == QtCore.Qt.Key_N:
            #  N - new line blink
            self.lineBlink()

            
    def hideElement(self):
        """
        Hides single element for given time.
        """
        self.regularList[self.y][self.x].setVisible(False)
        self.highlitList[self.y][self.x].setVisible(True)
        
        self.timer.singleShot(self.blinkTime, self.showElement )

    def showElement(self):
        """
        Shows signle element.
        """
        self.highlitList[self.y][self.x].setVisible(True)
        self.regularList[self.y][self.x].setVisible(True)     

    def play(self):
        """
        Start highlighting sequence.
        """
        
        self.playMode = True
        if self.treningMode:
            print "Look at: ", self.treningSequence[self.n]
        self.lineBlink()
        
    def lineBlink(self):
        """
        Each element in given line is highlighed. When it's
        the end of sequence it sends to decision function.
        """
        
        if self.count < len(self.sequence):
            
            present = self.sequence[self.count]
            flag = present[0]
            num = int(present[1])
            

            # Sets flag for plotting module
            checkPlot = open(self.checkPlotName,'w')           
            if self.count != 0: 
                checkPlot.write('1') # set newData flag
            elif self.count ==0:
                checkPlot.write('2') # set newSequence flag -> clear plots
            checkPlot.close()
            
            # Sets flag for analysis module
            checkAnalysis = open(self.checkAnalysisName,'w')
            checkAnalysis.write('1')
            checkAnalysis.close()


            tmp = present[0] + str(present[1]) + " " + str(time.time())
            self._set_hashtable_value("P300Blink", tmp)
            #~ self.plik.write(tmp + "\n")

            if flag == "r":
                for i in range(self.colNum):                    
                    self.regularList[num][i].setVisible(False)
                    self.highlitList[num][i].setVisible(True)
                    
                self.timer.singleShot(self.blinkTime, self.blinkEnd )        
                
            elif flag == "c":
                for i in range(self.rowNum):
                    
                    self.regularList[i][num].setVisible(False)
                    self.highlitList[i][num].setVisible(True)
             
                self.timer.singleShot(self.blinkTime, self.blinkEnd )  
        
        else:
            self.decision()
            
    def decision(self):
        """
        Choses whenever to use normal or trening decision function.
        Also, clears all counters and generets new random sequence.
        """
        temp = self.rowNum, self.colNum, self.repeat
        self.sequence = SequenceCreater(temp[0], temp[1], temp[2]).returnSequence()
        
        self.playMode = False
        self.count = 0

        self._set_hashtable_value( "P300Sequence", ' '.join(self.sequence) )
        
        if self.treningMode:
            self.treningDecision()

        elif self.normalMode:
            self.normalDecision()
            
    def treningDecision(self):
        """
        Trening decision.
        """
        
        c,r = self.treningSequence[self.n]
        l = self.textBank[int(r)*self.colNum+int(c)]
        self.menuBar.addLetter( l )
        self.n += 1
        
        # BEWARE!
        # If end a trening sequence, starts again.
        # just for testing purpose!
        if self.n==len(self.treningSequence): self.n=0
                
    def normalDecision(self):
        """
        Normal decision. Reads from file decision made by analysis
        module and prints letter on a menu bar.
        """
        
        # searches for decisionFile in it's direction
        name = self.decisionFile + "\n"
        while 1:
            p = popen('ls').readlines()
            if name in p: break

        f = open(self.decisionFile,'r')
        fileContent = f.readline()
        f.close()

        system('rm ' + self.decisionFile )
        print fileContent
        c, r = fileContent.rstrip().split()

        #~ r, c = 1,1
        square = self.textBank[int(r)*self.colNum+int(c)]
        if len(square) == 1:
            self.menuBar.addLetter( square )            
        elif square==u"SPACE" or square==u"ODSTĘP":
            self.menuBar.addLetter(" ")
        elif square==u"DEL" or square==u"USUŃ":
            self.menuBar.delLetter()
        elif square==u"CLEAR" or square==u"WYCZYŚĆ":
            self.menuBar.clearText()
        else:
            print "Undefined request. Can't do. Sorry... :( "

    def blinkEnd(self):
        """
        What is done when blink ends.
        """
        
        present = self.sequence[self.count]
        flag = present[0]
        num = int(present[1])

        if flag == "r":
            for i in range(self.colNum):
                self.regularList[num][i].setVisible(True)
                self.highlitList[num][i].setVisible(False)
                
        elif flag == "c":
            for i in range(self.rowNum):
                self.regularList[i][num].setVisible(True)
                self.highlitList[i][num].setVisible(False)
        
        self.count += 1
        if self.playMode:
            self.timer.singleShot(self.blinkInterval, self.lineBlink)
        
        if self.seqFinished:
            self.sequence = SequenceCreater().returnSequence()
    

#############################
## MAIN PROGRAM

class GUI( ):
    def __init__(self, parent=None):
        pass
        
    def run(self):
        "Initializing GUI."
       
        app = QtGui.QApplication(sys.argv)
        window = Main( )
        
        #window.showFullScreen()
        window.show()
        
        sys.exit(app.exec_())  


if __name__=="__main__":

    GUI().run()
