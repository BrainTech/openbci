#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Marian Dovgialo <marian.dowgialo@gmail.com>
#

import time 

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from HapticsControl import HapticStimulator



class HapticStimulatorControlPeer(ConfiguredMultiplexerServer):
    '''Class to control sensory stimulation'''
    @log_crash
    def __init__(self, addresses):
        super(HapticStimulatorControlPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR) #ADD THIS
        ids = self.config.get_param("id").split(":")
        vid, pid = [int('0x'+i, base=16) for i in ids]
        self.stim = HapticStimulator(vid, pid)
        self.ready()
        self.logger.info("HapticController init finished!")
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stim.close()
        
    def handle_message(self, mxmsg):
        '''gets message HAPTIC_CONTROL_MESSAGE, which contains:
        
            message Variable {
                required string key = 1;
                required string value = 2;
            }
            
            key - 'S' or 'B' - single haptic channel, or bulk
            value - for single channel - '1:1.0' - first channel 
            for 1 second 
            for bulk: '1,2:1.0,0.4' - activate channel 1 for 1 second
            and channel 2 for 0.4 seconds. Channels can be in any order'''
            
        if mxmsg.type == types.HAPTIC_CONTROL_MESSAGE:
            l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'S':
                self.logger.info('Activating single haptic channel')
                self.logger.info('K:{} V:{}'.format(l_msg.key, l_msg.value))
                chnl_s, time_s = l_msg.value.split(':') #strings
                self.stim.stimulate(int(chnl_s), float(time_s))
            if l_msg.key == 'B':
                self.logger.info('Activating multiple haptic channels')
                chnl_ls, time_ls = l_msg.value.split(':') #strings of lists
                 
                chnl = [int(i) for i in chnl_ls.split(',')]
                time = [float(i) for i in time_ls.split(',')]
                self.stim.bulk_stimulate(chnl, time)
        if mxmsg.type == types.LAUNCHER_COMMAND:
            self.logger.info('{}'.format(mxmsg.message))

if __name__ == "__main__":
    h=HapticStimulatorControlPeer(settings.MULTIPLEXER_ADDRESSES)
    h.loop()
    
