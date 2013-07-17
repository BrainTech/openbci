#-*- coding: utf-8 -*-

"""
TODO: make the message disappear during calibration
TODO: add some notification when searching for eyetrackers
TODO: eyetracker choice
TODO: save calibration data (but where?)
TODO: get rid of time.sleep
TODO: add animation (moving & shrinking)
TODO: remove logic from connector and view and put it in CalibrationLogic
TODO: remove communication from view and put it in connector
TODO: proper logging messages
"""

import signal
import sys

from tobii import eye_tracking_io
import tobii.eye_tracking_io.eyetracker
import tobii.eye_tracking_io.mainloop
import tobii.eye_tracking_io.browsing
import tobii.eye_tracking_io.types
import pygame.display

from obci.control.peer.configured_client import ConfiguredClient
from multiplexer import multiplexer_constants
#from obci.configs import settings
import logging
import threading
import random
import os.path
from PyQt4 import QtGui, QtCore


class EatException(Exception):
    pass

class EtrCalibrationTobii(ConfiguredClient):
    """
    MX peer which performs Tobii eyetracker calibration.
    """
    def __init__(self, addresses):
        super(EtrCalibrationTobii, self).__init__(addresses=addresses, type=multiplexer_constants.peers.CLIENT)
        self.logger.info("Starting EAT calibration...")
        self._init_signals()
        self.ready()

    def _init_signals(self):
        self.logger.info("Signal handler setup")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())

    def signal_handler(self):
        def handler(signum, _frame):
            self.logger.info("Got signal " + str(signum) + ": terminating")
            #
            sys.exit(-signum)
        return handler

    def run(self):
        _connector = CalibrationConnector()


class CalibrationLogic(object):
    pass

class CalibrationViewMainWidget(QtGui.QWidget):
    def __init__(self, eyetracker):
        super(CalibrationViewMainWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        label = QtGui.QLabel(u"Zostanie przeprowadzona kalibracja. Naciśnij spację.")
        
        box = QtGui.QHBoxLayout()
        box.addWidget(label)
        
        self.setLayout(box)
        self.eyetracker = eyetracker
        self.state = "waiting"
        self.points = []
        self.point = None

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_Space:
            
            self.do_calibration()
    
    def do_calibration(self):
        self.state = "calibrating"
        self.eyetracker.StartCalibration()
        self.points = [(0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9), (0.5, 0.5)]
        random.shuffle(self.points)
        self.next_point()
        
    def next_point(self):
        if self.points:
            self.point = self.points[0]
            self.points = self.points[1:]
        else:
            self.point = None
        self.repaint()
        if self.point:
            QtCore.QTimer.singleShot(1000, self.record_data)
            QtCore.QTimer.singleShot(4000, self.next_point)
        else:
            self.finish_calibration()
    
    def record_data(self):
        self.eyetracker.AddCalibrationPoint(eye_tracking_io.types.Point2D(self.point[0], self.point[1]))
        
    def finish_calibration(self):
        self.state = "finished"
        self.eyetracker.ComputeCalibration(self.compute_calibration_finished)

    def compute_calibration_finished(self, error, _r):
        if error == 0x20000502:
            print "CalibCompute failed because not enough data was collected"
        elif error != 0:
            print "CalibCompute failed because of a server error", error
        else:
            print "Great success!"
        self.eyetracker.StopCalibration(None)
    
    def save_calibration(self, error, data):
        calibration_file = open(os.path.expanduser("~/calib.bin"), "wb")
        calibration_file.write(data)
        calibration_file.close()
    
    def paintEvent(self, _event):
        if self.state == "calibrating" and self.point:
            painter = QtGui.QPainter(self)
            self.draw_point(painter, self.point[0], self.point[1])
    
    def draw_point(self, painter, x, y):
        w, h = self.width(), self.height()
        cx, cy = w * x, h * y
        r = 0.02 * h
        painter.setBrush(QtGui.QBrush(QtCore.Qt.green, QtCore.Qt.SolidPattern))
        painter.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))
    

class CalibrationView(QtGui.QApplication):
    def __init__(self, eyetracker):
        super(CalibrationView, self).__init__(sys.argv)
        self.main_window = CalibrationViewMainWidget(eyetracker)
        self.main_window.setWindowTitle('Calibration Window')
        self.main_window.showFullScreen()


class BrowseThread(threading.Thread):
    def __init__(self):
        super(BrowseThread, self).__init__()
        self.mainloop = None
        self.browser = None
        self.eyetracker_info = None
        self.discovery = threading.Condition()
        
    def run(self):
        self.mainloop = eye_tracking_io.mainloop.Mainloop()
        self.browser = eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop, self.browsing_callback)
        self.mainloop.run()
        self.browser.stop()
    
    def browsing_callback(self, _id, msg, eyetracker_info):
        logging.getLogger('eat_amplifier').info(str(msg))
        print "msg"
        if msg == 'Found':
            with self.discovery:
                logging.getLogger("eat_amplifier").info("Got eyetracker info: " + str(eyetracker_info))
                self.eyetracker_info = eyetracker_info
                self.discovery.notify()
    
    def kill(self):
        logging.getLogger("eat_amplifier").info("killed")
        self.browser.stop()
        self.mainloop.quit()


class ConnectThread(threading.Thread):
    def __init__(self, eyetracker_info):
        super(ConnectThread, self).__init__()
        self.mainloop = None
        self.eyetracker_info = eyetracker_info
        self.eyetracker = None
        self.established = threading.Condition()
    
    def run(self):
        self.mainloop = eye_tracking_io.mainloop.Mainloop()
        #eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop, self.eyetracker_info, self.eyetracker_callback)
        #self.eyetracker = DummyEtr.create_async(self.mainloop, self.eyetracker_info, self.eyetracker_callback)
        self.mainloop.run()
    
    def eyetracker_callback(self, _error, eyetracker):
        logging.getLogger('eat_amplifier').info("WHOA!")
        self.eyetracker = eyetracker
        
    def kill(self):
        self.mainloop.quit()


class CalibrationConnector(object):
    def __init__(self):
        self.logger = logging.getLogger("eat_amplifier")
        self.eyetracker_info = None
        self.eyetracker = None
        self.eyetracker_thread = None
        eye_tracking_io.init()
        self._detect_eyetracker()
        self._connect_to_eyetracker()
        self._wait_for_key()
        #self._perform_calibration()

    def _detect_eyetracker(self):
        browse_thread = BrowseThread()
        browse_thread.start()
        with browse_thread.discovery:
            browse_thread.discovery.wait(7)
            browse_thread.kill()
            if browse_thread.eyetracker_info:
                self.logger.info("Found")
                self.eyetracker_info = browse_thread.eyetracker_info
                print self.eyetracker_info
            else:
                self.logger.info("Timeoutd")
                raise EatException("No eyetracker found")
    
    def _connect_to_eyetracker(self):
        self.eyetracker_thread = ConnectThread(self.eyetracker_info)
        self.eyetracker_thread.start()
        eye_tracking_io.eyetracker.Eyetracker.create_async(self.eyetracker_thread.mainloop, self.eyetracker_thread.eyetracker_info, self.eyetracker_thread.eyetracker_callback)
        with self.eyetracker_thread.established:
            self.eyetracker_thread.established.wait(11)
            if self.eyetracker_thread.eyetracker:
                self.logger.info("Connectd")
                self.eyetracker = self.eyetracker_thread.eyetracker
            else:
                self.logger.info("Timeoutdd")
                raise EatException("Could not connect to eyetracker")
    
    def _wait_for_key(self):
        app = CalibrationView(self.eyetracker)
        app.exec_()
        self.eyetracker_thread.kill()


if __name__ == "__main__":
    #EtrCalibrationTobii(settings.MULTIPLEXER_ADDRESSES).run()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.NOTSET)
    connector = CalibrationConnector()
