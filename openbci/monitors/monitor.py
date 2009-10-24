#!/usr/bin/env python

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
        data = data[-512:]
    
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
        data = [(x - av) / 5 for x in data]

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
