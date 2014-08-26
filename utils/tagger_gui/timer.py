#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

class Timer(QtGui.QWidget):
    def __init__(self, value, parent):
        super(Timer, self).__init__(parent)
        self.label = QtGui.QLabel(self)
        self.init_value = value
        self.value = value
        self.update_timer_display()
        self.is_on=0
        
    def set_is_on(self):
        self.is_on=1

    def set_is_off(self):
        self.is_on=0

    def timer_stop_action(self):
        pass

    def set_stop_action(self, stop_action):
        self.timer_stop_action = stop_action

    def _parse_value_to_time(self, value):
        return "{:0>2d}:{:0>2d}:{:0>2d}".format(abs(value)/(60*60), abs(value)/60, abs(value)%60)

    def timerTick(self):
        self.value -= 1
        self.update_timer_display()
        if self.value <= 0:
            self.timer.stop()
            self.timer_stop_action()

    def clock_start(self):
        self.set_is_on()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerTick)
        self.timer.start(1000) 
        self.show()

    def clock_stop(self):
        self.set_is_off()
        self.timer.stop()
        self.update_timer_display()

    def update_timer_display(self):
        self.label.setText(self._parse_value_to_time(self.value))

    def clock_reset(self):
        self.value = self.init_value
        self.update_timer_display()

    def set_position(self, position):
        if position == 1:
            self.label.move(20, 15)
        elif position ==2:
            self.label.move(115, 15)