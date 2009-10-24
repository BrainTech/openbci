#!/usr/bin/env python

import cPickle
import numpy
import sys

from PyQt4 import QtCore, QtGui
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import variables_pb2

class Spectrum(QtGui.QWidget):
    colora = QtGui.QColor(127, 0, 127)
    colorb = QtGui.QColor(0, 0, 0)
    ms = 0.

    def __init__(self, channel_number):
        QtGui.QWidget.__init__(self, None)
	
        self.channel_number = channel_number

        timer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
        timer.start(250)

        self.setWindowTitle(self.tr("Spectrum of channel " + str(channel_number)))
        self.resize(680, 540)

        self.connection = connect_client(type = peers.MONITOR)
        self.sampling_rate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(self.colorb)

        data = self.connection.query(message = str(self.channel_number), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 5).message
        #d = cPickle.loads(data)
        vec = variables_pb2.SampleVector()
        vec.ParseFromString(data)
        d = []
        for x in vec.samples:
            d.append(x.value)
        print "DANE ",d
        d2 = d[-int(self.sampling_rate * 4):]
        d2 = abs(numpy.fft.rfft(d2))
        d2[0] = 0
        d2[1] = 0
        j = len(d2)
        for i in range(j):
            if i < 5 * 4 or i > 45  * 4:
                d2[i] = 0
        s = 0
        for x in range(7 * 4, 15 * 4):
            s += d2[x]
        self.ms = max(s, self.ms)
        m = max(d2)
        #print s
        d3 = [400. * x / m for x in d2]
        for i in xrange(len(d3)):
            if i % 8 == 0:
                painter.drawLine(10 + i, 90 - 3 * (i % 32), 10 + i, 100)
                painter.drawText(5 + i, 85 - 3 * (i % 32), str(i / 4))
        painter.setPen(self.colora)
        for i in xrange(len(d3)):
            painter.drawLine(10 + i, 100, 10 + i, 100 + int(d3[i]))
            if d3[i] > 100:
                painter.drawText(5 + i, 110 + int(d3[i]), str(i / 4.))
        painter.drawLine(620, 10 + self.ms / 30., 680, 10 + self.ms / 30.)
        painter.setBrush(QtCore.Qt.green)
        painter.drawRect(640, 10, 40, s / 30.)
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "<channel number>"
        sys.exit(1)

    app = QtGui.QApplication(sys.argv)
    spectrum = Spectrum(int(sys.argv[1]))
    spectrum.show()
    sys.exit(app.exec_())
