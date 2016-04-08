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


from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from threading import Thread
import os
import time
            
def test(logger):
    i = 0
    while True:
        i += 1
        print('\ntest thread, should print every second '+str(i))
        time.sleep(1)

class ThreadingTestPeer(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(ThreadingTestPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR)
        self.logger.info("ThreadingTestPeer init finished!")
        self.ready()
        
        Thread(target=test, args=(self.logger,)).start() #starting function which should print non stop
    
    def handle_message(self, mxmsg):
        if mxmsg.type == types.HAPTIC_CONTROL_MESSAGE:
            self.logger.info('GOT MESSAGE')
        self.no_response()

if __name__ == "__main__":
    ThreadingTestPeer(settings.MULTIPLEXER_ADDRESSES).loop()
    
    
