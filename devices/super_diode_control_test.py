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
import settings, cPickle, collections, variables_pb2, blinker_test, time, random


class SuperDiodeControl(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SuperDiodeControl, self).__init__(addresses=addresses, type=peers.SUPER_DIODE)
        #self.buffer_size = int(self.conn.query(message="DiodeCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.blinks = int(self.conn.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.blinkPeriod = float(self.conn.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                 
        self.buffer = collections.deque()
        

    def start_blinking(self, freqs):
        d = []
        [d.append(int(x)) for x in freqs]
        blinker_test.blink(d, 1, 1)
    
    def diodes_on(self):
        d = self.squares * [0]
        blinker_test.blink(d, 1, 1)
    
    def diodes_off(self):
        d = self.squares * [-1]
        blinker_test.blink(d, 1, 1)
    
    def generateSequence(self, blinks, squares):
        seq = []
        for i in range(squares):
            [seq.append(i) for x in range(blinks)]
        random.shuffle(seq)
        return seq


    def handle_message(self, mxmsg):
        if mxmsg.type == types.SWITCH_MODE:
            self.mode = self.conn.query(message="BlinkingMode", type=types.DICT_GET_REQUEST_MESSAGE).message
            if (self.mode.lower() == "SSVEP".lower()):
                self.diodes_on()
                #time.sleep(2)
                self.freqs = self.conn.query(message = "Freqs", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
                self.freqs = self.freqs.split(" ")
                for i in range(len(self.freqs)):
                    self.freqs[i] = int(self.freqs[i])
                self.start_blinking(self.freqs)
            elif (self.mode.lower() == "P300".lower()):
                self.diodes_off()
                 #time.sleep(2)
                self.blinks = int(self.conn.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                self.blinkPeriod = float(self.conn.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                self.seq = self.generateSequence(self.blinks, self.squares)
                s = ""
                for x in self.seq:
                    s += str(x) + ","
                s = s[:len(s) - 1]
                var = variables_pb2.Variable()
                var.key = "DiodSequence"
                var.value = s

                self.conn.send_message(message = var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)
                
                print "dc ds ", self.seq
                for x in self.seq:
                    blinker_test.blink_p300(x, self.blinkPeriod)
                    time.sleep(.75)
                    tstamp = time.time()
                    msg = variables_pb2.Blink()
                    msg.index = x
                        
                    msg.timestamp = tstamp
                    self.conn.send_message(message = msg.SerializeToString(), type = types.DIODE_MESSAGE, flush=True)
  
        self.no_response()


if __name__ == "__main__":
    SuperDiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()
