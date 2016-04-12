#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#      Marian Dovgialo <marian.dowgialo@gmail.com>
#

import time 
from threading import Thread
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash


class ThreadingTestSenderPeer(ConfiguredMultiplexerServer):
    '''Class to send test messages to thread testing receiver peer'''
    @log_crash
    def __init__(self, addresses):
        super(ThreadingTestSenderPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR)
        self.ready()
        t = Thread(target = self.generate_test_messages)
        t.start()
        self.logger.info("threading test sending peer init finished!")
    @log_crash
    def generate_test_messages(self):
        time.sleep(3)
        while True:
            msg = variables_pb2.Variable()
            msg.key = 'S'
            msg.value = '1:1.0'
            self.conn.send_message(message=msg.SerializeToString(), 
                          type=types.HAPTIC_CONTROL_MESSAGE,
                          flush=True)
            self.logger.info('Sending message!')
            time.sleep(4)
            
            
        
if __name__ == "__main__":
    ThreadingTestSenderPeer(settings.MULTIPLEXER_ADDRESSES)
    
    
