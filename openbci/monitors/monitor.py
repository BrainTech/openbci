#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#

import cPickle, numpy, sys, variables_pb2

from PyQt4 import QtCore, QtGui
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


class Monitor(QtGui.QWidget):
    colora = QtGui.QColor(128, 0, 128)
    colorb = QtGui.QColor(0, 0, 0)

    def __init__(self, channel_number):
        QtGui.QWidget.__init__(self, None)

        self.channel_number = channel_number

        timer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
        timer.start(100)

        self.setWindowTitle(self.tr("Monitor of channel " + str(channel_number)))
        self.resize(512, 512)

        self.connection = connect_client(type = peers.MONITOR)
        
        self.sampling_rate = int(self.connection.query(message="SamplingRate", \
            type=types.DICT_GET_REQUEST_MESSAGE).message)

    
    def average(self, data):
        sum = 0.
        for x in data:
            sum += x
        return sum / len(data)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(Monitor.colorb)

        data = self.connection.query(message = str(self.channel_number), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 5).message
        vec = variables_pb2.SampleVector()
        vec.ParseFromString(data)
        d = []
        for x in vec.samples:
            d.append(x.value) 	
        #data = cPickle.loads(data)
        #data = list(data)
        data = d
        data = data[-4 * self.sampling_rate:]
    
        # TO JEST FILTROWANIE 50HZ jesli FALSE to wylaczone
        filtruj = True
        if filtruj:
            data = numpy.fft.rfft(data)
            j = len(data)
            for i in range(j):
                if i > 40 * 4:
                    data[i] = 0.
            data = numpy.fft.irfft(data)
        
        av = self.average(data)
        data = [(x - av) / 5 for x in data][-512:]

        painter.drawLine(0, 512 / 2, 1024, 512 / 2)

        painter.setPen(Monitor.colora)
        start = (-100, 0)
        i = 0
        for j in data:
            j = int(256. + j / 1.)
            painter.drawLine(start[0], start[1], i, j)
            start = (i, j)
            i += 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "<channel number>"
        sys.exit(1)

    app = QtGui.QApplication(sys.argv)
    monitor = Monitor(int(sys.argv[1]))
    monitor.show()
    sys.exit(app.exec_())
