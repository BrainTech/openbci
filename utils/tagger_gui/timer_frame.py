#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from timer import Timer
from button import Button
from frame import Frame

class TimerFrame(Frame):
    def __init__(self):
        super(TimerFrame, self).__init__()

    def init_frame(self, params):
        self.duration=int(params['duration'])

        self.timer = Timer(self.duration, self)
        self.timer.set_position(1)
        self.timer.set_stop_action(self.action_stop)

        self.stop_button = Button('stop', self)
        self.stop_button.set_position(2)
        self.stop_button.connect(self.action_stop)

        self.set_off()

    def action_start(self):
        self.stop_button.set_enable()
        self.timer.clock_start()

    def action_stop(self):
        self.finish_action_elier_frame()
        if self.timer.is_on:
            self.timer.clock_stop()

        self.stop_button.set_disable()
        self.set_is_off()
        self.active_next_frame()

    def set_on(self):
        self.stop_button.set_enable()
        self.action_start()
        self.set_is_on()

    def set_off(self):
        if self.timer.is_on:
            self.timer.clock_stop()
            self.timer.clock_reset()
        self.stop_button.set_disable()
        self.set_is_off()

    def finish_frame_action(self):
        self.set_off()
        self.next_frame.remove(self.next_frame[0])