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
import sys

class HapticTestPeer(ConfiguredMultiplexerServer):
    '''
    Class for sending test control messages to Haptic stim
    '''
    @log_crash
    def __init__(self, addresses):
        super(HapticTestPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR)
        self.ready()
        t = Thread(target = self.generate_test_messages)
        t.start()
        self.logger.info("Haptics Test Peer init finished!")
    @log_crash
    def generate_test_messages(self):
        '''
        Generates test messages for Haptic stimulator
        tries to cover all possible combinations of stimulation
        '''
        time.sleep(3)
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '1:1.0'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('RUNNING! S1')
        time.sleep(4)
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '2:0.5'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('RUNNING! S2')
        time.sleep(4)
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '1,2:1.5,2.5'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('RUNNING! S1+2')
        time.sleep(4)
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '1:3'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('RUNNING! S1+2 in combination')
        time.sleep(1)
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '2:1'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        time.sleep(5)
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '1:10'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('RUNNING! S1')
        
        msg = variables_pb2.Variable()
        msg.key = 'S'
        msg.value = '5:1'
        self.conn.send_message(message=msg.SerializeToString(), 
                      type=types.HAPTIC_CONTROL_MESSAGE,
                      flush=True)
        self.logger.info('Sending wrong channel')
        time.sleep(5)
        sys.exit(0)
            
        
if __name__ == "__main__":
    HapticTestPeer(settings.MULTIPLEXER_ADDRESSES)
    
    
