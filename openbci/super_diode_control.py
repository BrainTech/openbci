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

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2, time, random
import blinker

from openbci.core import openbci_logging
LOGGER = openbci_logging.get_logger('super_diode_control')

DIODE_ON_FREQ = -1

class SuperDiodeControl(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SuperDiodeControl, self).__init__(addresses=addresses, type=peers.SUPER_DIODE)
        # an update request can be handled for config elements listed below:
        # save needed configuration.
        self.blinker = blinker.Blinker('/dev/ttyUSB0')
        self.blinker.open()
        self._init_freqs()
        self._init_mode()
        if self.mode == 'SSVEP':
            start = int(self.conn.query(message='SSVEP_RUNNING_ON_START', type=types.DICT_GET_REQUEST_MESSAGE).message)
            if start:
                self.start_blinking()
        else:
            raise Exception("Only SSVEP mode implemented!!!")

    def _init_mode(self):
        self.mode = self.conn.query(message="BlinkingMode", type=types.DICT_GET_REQUEST_MESSAGE).message

    def _init_freqs(self):
        freqs = self.conn.query(message = "Freqs", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        self.update_freqs(freqs)

    def update_freqs(self, freqs_str):
        freqs = freqs_str.split(" ")
        self.freqs = [0]*len(freqs)
        for i in range(len(freqs)):
            self.freqs[i] = int(freqs[i])

    def start_blinking(self):
        self.blinker.blinkSSVEP(self.freqs, 1, 1)
    
    def diodes_on(self):
        self.blinker.on()
    
    def diodes_off(self):
        self.blinker.off()
    
    def handle_message(self, mxmsg):
        if mxmsg.type == types.SWITCH_MODE:
            # get blinking mode config and start blinking
            self.check_mode_and_start_blinking()
        elif mxmsg.type == types.DIODE_UPDATE_MESSAGE:
            LOGGER.info("got message: " + str(mxmsg.type))
            l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            self.update_freqs(l_msg.value)
            if self.freqs[0] == -1:
                self.diodes_on()
            else:
                self.start_blinking()
            # this property can be updated by self, so set it in hashtable
            self.conn.send_message(message = mxmsg.message, type = types.DICT_SET_MESSAGE, flush=True)
            
            LOGGER.info("Mode: " + str(self.mode) + "  Freqs:  "+ str(self.freqs))
        elif mxmsg.type == types.SSVEP_CONTROL_MESSAGE and self.mode == 'SSVEP':
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'stop':
                LOGGER.info("Stop ssvep!")
                self.diodes_on()
            elif l_msg.key == 'start':
                LOGGER.info("Start ssvep!")
                self.start_blinking()

            else:
                LOGGER.warning("Unrecognised ssvep control message! "+str(l_msg.key))
        
            
        self.no_response()

if __name__ == "__main__":
    SuperDiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()
