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
    finish_signal = pyqtSignal()

    def __init__(self):
        super(TagGui, self).__init__()

    def initUI(self, frames_params, display_list):
        hbox = QtGui.QHBoxLayout(self)
        status_bar = StatusBar()
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        frames = {}
        for type_, name, params in frames_params:
            if type_ == 'timer':
                frames[name] = TimerFrame()
                frames[name].init_frame(params)
            elif type_ == 'tag':
                frames[name] = TagFrame()
                frames[name].init_frame(status_bar, self.tag_signal, params)

            splitter.addWidget(frames[name])

        frames['end'] = EndFrame()
        frames['end'].init_frame(self.finish_signal)
        splitter.addWidget(frames['end'])

        for ind, name in enumerate(display_list):
            if ind == 0:
                frames[name].set_is_first()
            else:
                frames[name].set_elier_frame(frames[display_list[ind-1]])

            if ind < len(display_list)-1:
                frames[name].set_next_frame(frames[display_list[ind+1]])

        frames[display_list[-1]].set_next_frame(frames['end'])
        frames['end'].set_elier_frame(frames[display_list[-1]])

        splitter.addWidget(status_bar)
        hbox.addWidget(splitter)
        self.setLayout(hbox)

        self.setWindowTitle('Tagger Manual')
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(200, 200, 410, len(frames)*55+40)
        self.show()
