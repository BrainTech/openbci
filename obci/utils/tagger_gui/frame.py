#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class Frame(QtGui.QFrame):
    def __init__(self):
        super(Frame, self).__init__()
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.is_on=0
        self.next_frame =[]
        self.elier_frame=[]

    def init_frame(self):
        pass

    def set_elier_frame(self, elier_frame):
        self.elier_frame.append(elier_frame)

    def set_next_frame(self, next_frame):
        self.next_frame.append(next_frame)

    def set_is_first(self):
        self.is_first=1
        self.set_on()

    def set_is_on(self):
        self.is_on=1

    def set_is_off(self):
        self.is_on=0

    def action_start(self):
        pass

    def action_stop(self):
        pass

    def set_on(self):
        pass

    def set_off(self):
        pass

    def active_next_frame(self):
        if len(self.next_frame):
            self.next_frame[0].set_on()

    def deactivation_next_frame(self):
        if len(self.next_frame):
            self.next_frame[0].set_off()

    def finish_action_elier_frame(self):
        self.elier_frame[0].finish_frame_action()
        self.elier_frame.remove(self.elier_frame[0])
    
    def finish_frame_action(self):
       pass