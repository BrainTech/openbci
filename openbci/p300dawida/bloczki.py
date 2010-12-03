# -*- coding: UTF-8 -*- 
from PyQt4 import QtGui, QtCore
import numpy as np
import sys
import time, random

import math

# made widgets
from widgets import MenuBar, RectangleArea



### LIST OF CONSTANTS
## fontSize        - text sizes
## backgroundColor - color of whole window
## rectColor       - color filling rectangles
## penWidth        - width of rectangle boundries
## blinkTime       - time length of blink period
## blinkInterval   - time interval beetwen two blinks
## repeat          - how many times should list be repeated
## count           - points present possition in sequence

## TEMPORARY
## playMode        - jak jest TRUE to cala sekwencja leci sruu
## seqFinished     - True, gdy cala lista zostanie przelecona





###########################
## Main window

class Main(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.window = QtGui.QMainWindow()

        
        ## Window options
        self.setWindowTitle("P300")
        self.text = "cos"
        
        self.screenWidth =self.window.width()
        self.screenHeight = self.window.height()
        
        ## Some temporary flags
        self.playMode = False
        self.seqFinished = False
        
        ## Constants
        self.numOfRows  = 5
        self.numOfCols  = 10
        self.menuFontSize = 20
        
        self.fontColor = fC = QtGui.QColor(0xffffff)
        self.bgColor = bgC = QtGui.QColor(0x222222) # RGB
        self.rectColor = txC = QtGui.QColor(0x00FFFF) 
        
        self.penWidth = 3
        self.blinkInterval = 500
        self.blinkTime = 300  # ms
        self.repeat = 2
        self.count = 0
        
        self.rectSize = (60, 60)
        
        ## select languale (?)
        # pol - Polish
        # eng - English
        self.language = "eng"
        self.textBank = self.letterBank()
    
        
            
#        self.letterBank = self.letterBank.decode('UTF-8')
#        print "after: ", self.letterBank
        
        ## Offset values - not using temporary
        self.menuHeight = 0.1*self.screenHeight
        self.topOffset = 0.1*self.screenHeight
        self.bottomOffset = 0.1*self.screenHeight
        self.leftOffset = 0.1*self.screenWidth
        self.rightOffset = 0.1*self.screenWidth
        self.spacing = 10
        
        
        ## Defining sequence list
        temp = self.numOfRows, self.numOfCols, self.repeat
        self.sequence = SequenceCreater(temp[0], temp[1], temp[2]).returnSequence()
        
        
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
        
        for y in range(self.numOfRows):
            
            ## This makes list in form of a matrix
            self.letters.append( list() )
            self.regularList.append( list() )
            self.highlitList.append( list() )
            
            
            for x in range(self.numOfCols):
                command = ""
                
                
                text = self.textBank[y*self.numOfCols + x]
                
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
        

    def letterBank(self):
        "Creates list of text filling rectangles."
        
        polishAlphabet = u'AĄBCĆDEĘFGHIJKLŁMNŃOÓPRSŚTUWYZŹŻ' # len = 32
        latinAlphabet = u'ABCDEFGHIKLMNOPQRSTVXYZ' # len = 23
        funcWordEng = [u"DEL", u"SPACE", u"CLEAR"] # len = 3
        funcWordPol = [u"USUŃ", u"ODSTĘP", u"WYCZYŚĆ"] # len = 3
        numCharacters = u'0123456789' # len = 10
        characters = u'?,.!' # len = 5
        functionChars = [u'message', u'func_2', u'func_3', u'func_4'] # len = ?
        
        
        length = self.numOfRows * self.numOfCols
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
                for num in numCharacters:
                    charList.append(num)
                
                for char in latinAlphabet:
                    charList.append(char)
                
                for char in characters:
                    charList.append(char)
                    
                if len(charList) < length:
                    charList.insert(-len(funcWordPol), u'message')
                    
                for func in funcWordEng:
                    charList.append(func)
                    
                while(len(charList) < length ):
                    charList.insert(-len(funcWordPol),"func")
        
        return charList
    
    def resizeEvent(self, event):
        "What is done, when window changes its size."
        #print self.size()
        self.menuBar.update()
            
        

    def keyPressEvent(self, event):
        "After key is pressed."
        
        if event.key() == QtCore.Qt.Key_Escape:
            # ESC to shut down program
            quit()  
            
        elif event.key() == QtCore.Qt.Key_Tab:
            # TAB - RANDOM HIGHLIGHT
            self.y = random.randint(0, self.numOfRows-1)
            self.x = random.randint(0, self.numOfCols-1)
            
            print "x: ", self.x, " y: ", self.y
            
            self.hideElement()            
            
        elif event.key() == QtCore.Qt.Key_P:
            self.play()
            
        elif event.key() == QtCore.Qt.Key_R:
            # R - RANDOM
            self.y = random.randint(0, self.numOfRows-1)
            self.x = random.randint(0, self.numOfCols-1)
            
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
        "Hidding part of a blink."
        
        self.regularList[self.y][self.x].setVisible(False)
        self.highlitList[self.y][self.x].setVisible(True)
        
        self.timer.singleShot(self.blinkTime, self.showElement )

    def showElement(self):
        "Back_to_normal part of a blink."
        self.highlitList[self.y][self.x].setVisible(True)
        self.regularList[self.y][self.x].setVisible(True)     

    def play(self):
        self.playMode = True
        self.lineBlink()
        
    def lineBlink(self):
        
        ## TO DO:
        ## more efficient statement?
        
        if self.count < len(self.sequence):
            present = self.sequence[self.count]
            flag = present[0]
            num = int(present[1])
    
            if flag == "r":
                for i in range(self.numOfCols):
                    
                    self.regularList[num][i].setVisible(False)
                    self.highlitList[num][i].setVisible(True)
                    
                self.timer.singleShot(self.blinkTime, self.blinkEnd )        
                
            elif flag == "c":
                for i in range(self.numOfRows):
                    
                    self.regularList[i][num].setVisible(False)
                    self.highlitList[i][num].setVisible(True)
             
                self.timer.singleShot(self.blinkTime, self.blinkEnd )  
        
        else:
            self.seqFinished = True
                
    def blinkEnd(self):
        
        present = self.sequence[self.count]
        flag = present[0]
        num = int(present[1])

        if flag == "r":
            for i in range(self.numOfCols):
                
                self.regularList[num][i].setVisible(True)
                self.highlitList[num][i].setVisible(False)
                
        elif flag == "c":
            for i in range(self.numOfRows):
                
                self.regularList[i][num].setVisible(True)
                self.highlitList[i][num].setVisible(False)
        
        self.count = self.count + 1
        if self.playMode:
            self.timer.singleShot(self.blinkInterval, self.lineBlink)
        
        if self.seqFinished:
            self.sequence = SequenceCreater().returnSequence()
        

    
    
#########################################
#### Other moduls

class SequenceCreater():
    """This class create a random sequence of blinks."""
    
    def __init__(self,numOfRows, numOfCols, repeat):
        
        self.numOfRows = numOfRows
        self.numOfCols = numOfCols
        self.repeat = repeat
                
        self.createSequence()
        self.randomizeSequence()
        
        print self.sequence 
    
    def createSequence(self):
        "Creates sequence list"
        self.sequence = list()
        
        # Adds row* tuple(r,num) and col*tuple(c,num)
        # where r- is row, and c - is column
        for i in range(self.numOfRows):
            self.sequence.append( ("r", i) )
        for j in range(self.numOfCols):
            self.sequence.append( ("c", j) )
         
        # Repeats the same list 'repeat' times
        self.sequence = self.sequence*self.repeat
    
    def randomizeSequence(self):
        "Shuffles sequence"
        
        np.random.shuffle(self.sequence)
        for i in range(len(self.sequence)-1):
            
            # Check if any tuple is same as next one.
            # If not, shuffle list again.
            if self.sequence[i]==self.sequence[i+1]:
                self.randomizeSequence()
                
    def returnSequence(self):
        return self.sequence
     
    

#############################
## MAIN PROGRAM

class GUI( ):
    def __init__(self, parent=None):
        self.columns = 10
        self.rows = 5
        
    
    def run(self):
        "Initializing GUI."
        app = QtGui.QApplication(sys.argv)
        window = Main( )
        
        #window.showFullScreen()
        window.show()
        
        sys.exit(app.exec_())  
        


if __name__=="__main__":
    
    GUI().run()
    
    
    
    
