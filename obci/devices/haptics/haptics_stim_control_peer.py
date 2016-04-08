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
from obci.devices.haptics.HapticsControl import HapticStimulator
import os, sys

class HapticStimulatorControlPeer(ConfiguredMultiplexerServer):
    '''Class to control sensory stimulation'''
    @log_crash
    def __init__(self, addresses):
        super(HapticStimulatorControlPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR)
        ids = self.config.get_param("id").split(":")
        vid, pid = [int(i, base=16) for i in ids]
        # to report for errors before giving device to control proces
        self.stim = HapticStimulator(vid, pid)
        self.ready()
        self.logger.info("HapticController init finished!")
    
    def close(self):
        del self.stim
        
    def handle_message(self, mxmsg):
        '''Receives message HAPTIC_CONTROL_MESSAGE and sends it
        to stimulation board control process.
        
        Message contains info of type::
            
                message Variable {
                    required string key = 1;
                    required string value = 2;
                    }
        
        :param key: - 'S', 'B' or 'T' - Single haptic channel or
        Bulk - multiple channel to activate. 'T' - to terminate FTDI
        control process and release device
        :param value: - for single channel - '1:1.0' - first channel 
        for 1 second. For bulk: '1,2:1.0,0.4' - activate channel 1 for
        1 second and channel 2 for 0.4 seconds. Channels can be in any
        order'''
            
        if mxmsg.type == types.HAPTIC_CONTROL_MESSAGE:
            l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'S':
                chnl_s, time_s = l_msg.value.split(':') #strings
                self.logger.info('Activating haptic msg:\n{}'.format(l_msg))
                self.stim.stimulate(int(chnl_s), float(time_s))
            if l_msg.key == 'B':
                logs = 'Activating multiple haptic channels msg: {}'.format(l_msg)
                self.logger.info(logs)
                chnl_ls, time_ls = l_msg.value.split(':') #strings of lists 
                chnl = [int(i) for i in chnl_ls.split(',')]
                time = [float(i) for i in time_ls.split(',')]
                self.stim.bulk_stimulate(chnl, time)
            if l_msg.key == 'T':
                self.logger.info('Shutting down')
                self.stim.close()
                sys.exit(0)
        self.no_response()

if __name__ == "__main__":
    HapticStimulatorControlPeer(settings.MULTIPLEXER_ADDRESSES).loop()
    
    
