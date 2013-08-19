#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import QObject, pyqtSignal
from PyQt4 import QtGui, QtCore


class TagGui(QtGui.QMainWindow):
    tag = pyqtSignal(str)
    def __init__(self, buttonNames):
        super(TagGui, self).__init__()
        self.buttons = [''] * len(buttonNames)
        #self.nrButton = nrButton
        self.buttonNames = buttonNames
        self.x = 30
        self.y = 50
        self.initUI()
        
    def center(self):        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def createButtons(self):
        for index, name in enumerate(self.buttonNames):
            self.buttons[index] = QtGui.QPushButton(name, self)
            self.buttons[index].move(self.x, self.y)
            self.buttons[index].clicked.connect(self.buttonClicked)
            self.x += 120            

    def initUI(self):
        self.setGeometry(300, 300, 60 + len(self.buttonNames) * 120, 150)
        self.setWindowTitle('Tags Creator')
        self.center()
        self.createButtons()
        self.statusBar()
        self.show()

    def buttonClicked(self):
      
        sender = self.sender()
        for name in self.buttonNames:
            if sender.text() == name:
                self.statusBar().showMessage('{} tag was created'.format(sender.text()))
                self.tag.emit(str(name))

def run():
    app = QtGui.QApplication(sys.argv)
    print('a')
    ex = TagGui(['w', 'a', 'r', 'y', 't'])
    print('b')
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
