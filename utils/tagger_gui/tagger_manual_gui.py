#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

from timer_frame import TimerFrame
from tag_frame import TagFrame
from end_frame import EndFrame
from PyQt4.QtCore import pyqtSignal

from obci.acquisition.acquisition_helper import get_file_path


class StatusBar(QtGui.QStatusBar):
    def __init__(self):
        super(StatusBar, self).__init__()
        self.isSizeGripEnabled()

    def show_message(self, message):
        self.showMessage(message, 1000)


class TagGui(QtGui.QWidget):
    tag_signal = pyqtSignal(str)
    def __init__(self):
        super(TagGui, self).__init__()

    def initUI(self, frames_params):
        hbox = QtGui.QHBoxLayout(self)

        status_bar = StatusBar()

        frames = []
        for type_, params in frames_params:
            if type_ == 'timer':
                frames.append(TimerFrame())
                frames[-1].init_frame(params)
            elif type_ == 'tag':
                frames.append(TagFrame())
                frames[-1].init_frame(status_bar, self.tag_signal, params)
        print frames

        frames.append(EndFrame())
        frames[-1].init_frame()

        for ind, f in enumerate(frames):
            if ind == 0:
                f.set_is_first()
            else:
                f.set_elier_frame(frames[ind-1])

            if ind < len(frames)-1:
                f.set_next_frame(frames[ind+1])


        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        for f in frames:
            splitter.addWidget(f)

        splitter.addWidget(status_bar)
        hbox.addWidget(splitter)
        self.setLayout(hbox)

        self.setWindowTitle('Tagger Manual')
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(200, 200, 410, len(frames)*55+40)
        self.show()
