# -*- coding: UTF-8 -*- 
from PyQt4 import QtGui, QtCore
###################################
## Widgets

class MenuBar(QtGui.QWidget):
    """
    This class is resposible for MenuBar widget acting.
    It only displays text which it recives.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
            
        
        self.text = QtCore.QString()
        
        self.setBackgroundRole(QtGui.QPalette.Base)
        #self.fontSize = float(fontSize)
        
        ## DialogBox shows letters.
        self.dialogBox = QtGui.QTextEdit(self)
        self.dialogBox.resize(1000,200)
        self.dialogBox.setReadOnly(True)
        #self.dialogBox.acceptRichText()
        #self.dialogBox.setFontPointSize(self.fontSize)
        

        
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)
        
    def sizeHint(self):
        return QtCore.QSize(100, 100)
        
    def setFontSize(self, size):
        self.dialogBox.setFontPointSize(size)
        self.update()
        
    def setFontColor(self, color):
        self.dialogBox.setTextColor(color)
        self.update()

    def addLetter(self, letter):
        
        self.text += letter
        print self.text
        self.dialogBox.setText(self.text)

    def delLetter(self):
        self.text = self.text[:-1]
        print self.text
        self.dialogBox.setText(self.text)
    
    def spaceLetter(self):
        self.text = self.text + " "

    def clearText(self):
        self.text = ""
        self.dialogBox.setText(self.text)
        
      
class RectangleArea(QtGui.QWidget):
    """
    This class provides look of boxes with letters.
    It takes four arguments:
    text - letters which will be shown
    flag - if 'r' then block behaves as REGULAR, when it's 'h
            then it describes HIGHLIGHTED block.
    bgC  - is a background color.
    txC  - is a font color.
    Becasue this class uses drawEvent, for the sake of clean
    looking console output, is't not good to use another such
    event in any other class.
    """
    def __init__(self, text, flag, bgC, txC, size, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        
        
        self.penWidth = 5
        
        if len(text)>1:
            self.fontSize = 12
        else:
            self.fontSize = 20
        
        self.text =text
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.bgColor = bgC
        self.txColor = txC
        self.width  = size[0]
        self.height = size[1]
        
        rectSize = QtCore.QSizeF(size[0], size[1])
        rectPos  = QtCore.QPointF(10, 10)
        self.rectangle = QtCore.QRectF(rectPos, rectSize)
        
        
        ## Depening on flag, widget is in either normal colors (r),
        ## or highlit (h), which are reversed colors.
        if flag == 'h':
            self.penColor = self.bgColor
            self.rectColor = self.txColor
        elif flag == 'r':
            self.penColor = self.txColor
            self.rectColor = self.bgColor
        
        
    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)
        
    def sizeHint(self):
        return QtCore.QSize(100, 100)
        
        
    def setPenColor(self, color):
        self.penColor = color
        self.update()
        
    def setBgColor(self, color):
        self.brushColor = color
        self.update()
        
    def setFontSize(self, size):
        self.fontSize = size
        self.update()
    
    def setPenWidth(self, width):
        self.penWidth = width
        self.update()
        
    def setIcon(self, painter):
        objectName = self.text

        self.iconPath = QtGui.QPainterPath()
        
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)     
        
        if objectName == QtCore.QString(u"message"):
            ## This is responsible for that cute envelope thing.
            left = self.width*0.3
            right = self.width
            top = self.height*0.4
            bottom = self.height*0.8
            self.iconPath.moveTo(left,top)
            self.iconPath.lineTo(right,top)
            self.iconPath.lineTo(right,bottom)
            self.iconPath.lineTo(left,bottom)
            self.iconPath.lineTo(left,top)
            self.iconPath.lineTo(right,bottom)
            self.iconPath.moveTo(right,top)
            self.iconPath.lineTo(left,bottom)
            
            
            
            self.pen.setWidth(2)
            self.pen.setColor( self.penColor )
            self.brushColor = QtGui.QBrush(self.rectColor)
        
            painter.setPen( self.pen )
            painter.setBrush(self.brushColor)    
            painter.drawPath(self.iconPath)   
            painter.translate(80,80)        
            
            
        else:
            
            font = QtGui.QFont("Times", self.fontSize)
            font.setStyleStrategy(QtGui.QFont.ForceOutline)
    
            self.pen.setWidth(1)
            self.pen.setColor( self.penColor )
                        
            painter.setFont( font )
            self.text = QtCore.QString(self.text)
            self.brushColor = QtGui.QBrush(self.penColor)
            
            painter.setPen( self.pen )
            painter.setBrush(self.brushColor)
            painter.drawText(self.rectangle, QtCore.Qt.AlignCenter, self.text)
            
            



        painter.end()
        
    def paintEvent(self, event):
        
        ### TO DO:
        ### POSPRZATAC TA FUNKCJE !!!!!!
        
        self.rectPainter = QtGui.QPainter()
        self.pen = QtGui.QPen()        

        
        ## Drawing rectangular figure.
        self.rectPainter.begin(self)
        self.rectPainter.setRenderHint(QtGui.QPainter.Antialiasing)
        
            ## Pen is rectangle's rim
        self.pen.setColor( self.penColor )
        self.pen.setWidth( self.penWidth )
        
        self.rectPainter.setPen(self.pen)
        
            ## Brush is filling of rectangle
        self.rectPainter.setBrush(QtGui.QBrush( self.rectColor ))
        
        
        self.rectPainter.drawRoundedRect( self.rectangle, 15, 15)
        self.rectPainter.end()
        
        
        
        ## Placing text in center of each rectangle
        objectPainter = QtGui.QPainter()
        
        self.setIcon(objectPainter)
        