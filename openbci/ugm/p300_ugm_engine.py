#!/usr/bin/env python
# -*- coding: utf-8 -*-
import thread, time, random
from ugm import ugm_engine
from ugm import ugm_config_manager
from ugm import p300_config_manager
import ugm_logging as logger
LOGGER = logger.get_logger("p300_ugm_engine")

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


from PyQt4 import QtCore, QtGui, Qt


class P300UgmEngine(ugm_engine.UgmEngine):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh."""
    def __init__(self):
        """Store config manager."""
        super(P300UgmEngine, self).__init__(ugm_config_manager.UgmConfigManager('black'))

    def run(self):
        """Fire pyqt application with UgmMainWindow. 
        Refire when app is being closed. (This is justified as if 
        ugm_config_manager has changed its state remarkably main window
        needs to be completely rebuilt."""
        #thread.start_new_thread(self._start_blinking, ())
        class Thread(QtCore.QThread):
            def __init__(self, engine):
                super(Thread, self).__init__(engine)
                self._engine = engine
            def run(self):
                self._engine._start_blinking()

        self.start_blinking_timer = QtCore.QTimer(self)
        self.start_blinking_timer.setSingleShot(True)
        QtCore.QObject.connect(self.start_blinking_timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("_blink()"))
        self.start_unblinking_timer = QtCore.QTimer(self)
        self.start_unblinking_timer.setSingleShot(True)
        QtCore.QObject.connect(self.start_unblinking_timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("_unblink()"))

        Thread(self).start()

        super(P300UgmEngine, self).run()

    def _start_blinking(self):
        LOGGER.info("_start_blinking fired...")
        self.connection = connect_client(type = peers.TAGS_SENDER)
        # num of blinks per square
        self.rows = int(self.connection.query(message = "P300Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.cols = int(self.connection.query(message = "P300Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.blinkMode = self.connection.query(message = "P300BlinkMode", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        self.blinkPeriod = float(self.connection.query(message = "P300BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.blinkBreak = 1000.0*float(self.connection.query(message = "P300BlinkBreak", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)         

        sq_size = float(self.connection.query(message = "P300SquareSize", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        font_size = int(self.connection.query(message = "P300FontSize", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        letters = self.connection.query(message = "P300Letters", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message.split(' ')
        LOGGER.info("Got data from hashtable in start_blinking.")        

        self._p300_config_manager = p300_config_manager.P300ConfigManager()
        config = self._p300_config_manager.generate_config(self.rows, self.cols, sq_size, font_size, letters, self.blinkMode)
        self._config_manager.set_full_config(config)
        self.rebuild()
        LOGGER.info("Finish rebuilding engine.")

        self.next_blink_rows = True
        self.to_unblink = None
        self.start_blinking_timer.start(self.blinkBreak)
                       
    @QtCore.pyqtSlot()
    def _blink(self):
        LOGGER.info("BLINK")

        if self.next_blink_rows:
            ind = random.randint(0, self.rows-1)
            blinked, non_blinked = self._p300_config_manager.get_blink_row(ind)
        else:
            ind = random.randint(0, self.cols-1)
            blinked, non_blinked = self._p300_config_manager.get_blink_col(ind)
            
        self.next_blink_rows = not self.next_blink_rows
        self.to_unblink = non_blinked

        for stim in blinked:
            self._config_manager.set_config(stim)
        self.update()
        QtCore.QTimer.singleShot(self.blinkPeriod, self, QtCore.SLOT("_unblink()"))

    @QtCore.pyqtSlot()
    def _unblink(self):
        LOGGER.info("UNBLINK")
        
        for stim in self.to_unblink:
            self._config_manager.set_config(stim)
        self.update()
        QtCore.QTimer.singleShot(self.blinkBreak, self, QtCore.SLOT("_blink()"))  
