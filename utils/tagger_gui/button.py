#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class Button(QtGui.QPushButton):
    def __init__(self, button_name, parent):
        super(Button, self).__init__(button_name, parent)

    def set_disable(self):
        self.setEnabled(False) 

    def set_enable(self):
        self.setEnabled(True)

    def set_position(self, position):
        if position == 1:
            self.move(10, 10)
        elif position ==2:
            self.move(100,10)
        elif position == 3:
            self.move(200, 10)
        elif position == 4:
            self.move(300, 10)
        elif position == 5:
            self.move(150, 10)
            
    def connect(self, func_action):
        self.clicked.connect(func_action)