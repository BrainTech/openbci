#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from button import Button

class EndFrame(QtGui.QFrame):
    def __init__(self):
        super(EndFrame, self).__init__()
        self.setFrameStyle(QtGui.QFrame.Plain)#setFrameShape(QtGui.QFrame.StyledPanel)
        self.is_on=0
        self.elier_frame=[]

    def init_frame(self, finish_signal):
        self.finish_signal = finish_signal
        self.finish_button = Button('Finish', self)
        self.finish_button.set_position(5)
        self.finish_button.connect(self.finish_action_elier_frame)
        self.set_off()

    def set_elier_frame(self, elier_frame):
        self.elier_frame.append(elier_frame)

    def set_is_on(self):
        self.is_on=1

    def set_is_off(self):
        self.is_on=0

    def set_on(self):
        self.finish_button.set_enable()
        self.set_is_on()

    def set_off(self):
        self.finish_button.set_disable()
        self.set_is_off()

    def finish_action_elier_frame(self):
        self.elier_frame[0].finish_frame_action()
        self.elier_frame.remove(self.next_frame[0])
        self.set_off()
        self.finish_signal.emit()
