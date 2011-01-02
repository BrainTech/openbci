#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import thread, time, random
from ugm import ugm_engine
from ugm import ugm_config_manager
from ugm import p300_config_manager
import ugm_logging as logger
LOGGER = logger.get_logger("p300_ugm_engine")

from tags import tagger
TAGGER = tagger.get_tagger()

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import variables_pb2
import sys

from PyQt4 import QtCore, QtGui, Qt


class P300TestUgmEngine(ugm_engine.UgmEngine):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh."""
    def __init__(self):
        """Store config manager."""
        super(P300TestUgmEngine, self).__init__(ugm_config_manager.UgmConfigManager('black'))

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

        self.connection = connect_client(type = peers.UGM)

        Thread(self).start()

        super(P300TestUgmEngine, self).run()

    def _start_blinking(self):
        LOGGER.info("_start_blinking fired...")
        # num of blinks per square
        self.rows = int(self.connection.query(message = "P300Rows", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.cols = int(self.connection.query(message = "P300Cols", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.blinkPeriod = 1000*float(self.connection.query(message = "P300BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.blinkBreak = 1000*float(self.connection.query(message = "P300BlinkBreak", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)         
        blink_mode = self.connection.query(message = "P300BlinkMode", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        blink_color = self.connection.query(message = "P300BlinkColor", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        sq_size = float(self.connection.query(message = "P300SquareSize", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        font_size = int(self.connection.query(message = "P300FontSize", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        letters = self.connection.query(message = "P300Letters", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message.split(' ')
        self.trainingBlinksPerChar = int(self.connection.query(message = "P300TrainingBlinksPerChar", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.trainingCharBreak = 1000*float(self.connection.query(message = "P300TrainingCharBreak", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        self.trainingChars = self.connection.query(message = "P300TrainingChars", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message.split(' ')
        self.trainingChars.reverse()

        LOGGER.info("Got data from hashtable in start_blinking.")        

        self._p300_config_manager = p300_config_manager.P300ConfigManager()
        config = self._p300_config_manager.generate_config(self.rows, self.cols, sq_size, font_size, letters, blink_mode, blink_color)
        self._config_manager.set_full_config(config)
        self.rebuild()
        LOGGER.info("Finish rebuilding engine.")

        self.to_unblink = None
        self._blink_inds = [i for i in range(self.rows + self.cols)]
        random.shuffle(self._blink_inds)
        self._blink_ind = -1
        self._run_blinks = 0
        time.sleep(1)

#        self._init_target_letters(letters)
        self._training_next_char()
        self.start_blinking_timer.start(self.trainingCharBreak)
    def _init_target_letters(self, letters):
        self._targets = {}
        for char in self.trainingChars:
            ind = letters.index(char)
            row = ind/self.cols
            col = self.rows + (ind % self.cols)
            self._targets[char] = [row, col]

    def _ind_is_target(self, ind, char):
        return ind in self._targets[char]

    def _training_next_char(self):
        #try:
        #    char = self.trainingChars.pop()
        #except IndexError:
        #    LOGGER.info("END OF TRAINING")
        #    sys.exit(0)
        #else:
        #    stim = self._p300_config_manager.get_text(char)
        #    self._config_manager.set_config(stim)
        #    self.update()
        #    self.targetChar = char
        pass
            
    def _next_blink_ind(self):
        self._blink_ind += 1
        self._run_blinks += 1
        if self._blink_ind == self.rows + self.cols:
            random.shuffle(self._blink_inds)
            #r_ind = 1
            #c_ind = 2
            #while abs(r_ind-c_ind) == 1:
            #    random.shuffle(self._blink_inds)
            #    r, c = self._targets[self.targetChar]
            #    r_ind = self._blink_inds.index(r)
            #    c_ind = self._blink_inds.index(c)
            
            self._blink_ind = 0

        return self._blink_inds[self._blink_ind]

    @QtCore.pyqtSlot()
    def _blink(self):
        LOGGER.debug("BLINK")
        t0 = time.time()
        ind = self._next_blink_ind()
        if ind >= self.rows:
            blinked, non_blinked = self._p300_config_manager.get_blink_col(ind-self.rows)
        else:
            blinked, non_blinked = self._p300_config_manager.get_blink_row(ind)

        self.to_unblink = non_blinked

        for stim in blinked:
            self._config_manager.set_config(stim)
        self.update()

        t = time.time()   

     
        msg = variables_pb2.Blink()
        msg.index = ind
        msg.timestamp = t
        self.connection.send_message(message = msg.SerializeToString(), type = types.BLINK_MESSAGE, flush=True)

        #QtCore.QTimer.singleShot(self.blinkPeriod - 1000*(time.time() - t), self, QtCore.SLOT("_unblink()"))
        QtCore.QTimer.singleShot(25, self, QtCore.SLOT("_unblink()"))

    @QtCore.pyqtSlot()
    def _unblink(self):
        LOGGER.debug("UNBLINK")
        t0 = time.time()
        for stim in self.to_unblink:
            self._config_manager.set_config(stim)
        self.update()

        t = time.time()        
        #msg = variables_pb2.Blink()
        #msg.timestamp = t
        #self.connection.send_message(message = msg.SerializeToString(), type = types.BLINK_MESSAGE, flush=True)
#        TAGGER.send_tag(t0, t, "non-blink")

        #QtCore.QTimer.singleShot(self.blinkBreak - 1000*(time.time() - t), self, QtCore.SLOT("_blink()"))  
        if self._run_blinks < self.trainingBlinksPerChar:
            QtCore.QTimer.singleShot(150, self, QtCore.SLOT("_blink()"))  
        else:
            self._run_blinks = 0
            self._training_next_char()
            QtCore.QTimer.singleShot(self.trainingCharBreak, self, QtCore.SLOT("_blink()"))  
