#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Marian Dovgialo <marian.dowgialo@gmail.com>
#

import time 
from threading import Thread
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from HapticsControl import HapticStimulator


class HapticTestPeer(ConfiguredMultiplexerServer):
    '''Class to control sensory stimulation'''
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
        while True:
            msg = variables_pb2.Variable()
            msg.key = 'S'
            msg.value = '1:1.0'
            self.conn.send_message(message=msg.SerializeToString(), 
                          type=types.HAPTIC_CONTROL_MESSAGE,
                          flush=True)
            self.logger.info('RUNNING! S1')
            time.sleep(2)
            msg = variables_pb2.Variable()
            msg.key = 'S'
            msg.value = '2:0.5'
            self.conn.send_message(message=msg.SerializeToString(), 
                          type=types.HAPTIC_CONTROL_MESSAGE,
                          flush=True)
            self.logger.info('RUNNING! S2')
            time.sleep(2)
            
            msg = variables_pb2.Variable()
            msg.key = 'B'
            msg.value = '1,2:0.5,1.5'
            self.conn.send_message(message=msg.SerializeToString(), 
                          type=types.HAPTIC_CONTROL_MESSAGE,
                          flush=True)
            self.logger.info('RUNNING! S1+2')
            time.sleep(2)
        
if __name__ == "__main__":
    h=HapticTestPeer(settings.MULTIPLEXER_ADDRESSES)
    
    
