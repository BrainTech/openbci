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
from HapticsControl import HapticStimulator
from multiprocessing import Process, Pipe
import os

PIPETIMEOUT = 3

def controlProcess(vid, pid, conn):
    '''Process to control Stimulator.
    
    Stimulator relies on threads to work,
    peer blocks threads while waiting for message
    Should terminate when its parrent dies.
    To do that it checks if it became a child of init (ID==1)
    
    :param vid: USB VID of controlled device int or hex NOT string
    :param pid: USB PID of controlled device int or hex NOT string
    :param conn: receiving end of Pipe, to read control messages through
    '''
    
    stim = HapticStimulator(vid, pid)
    while True:
        if conn.poll(PIPETIMEOUT):#check if any data is sent, if not 
                                  #sent for some time check parentID
                                  #if 1 terminate 
                                  #(to check if parent died and close)
                                  #BREAKES WINDOWS COMPATABILITY
        
            l_msg = conn.recv()
            
            if l_msg.key == 'S':
                chnl_s, time_s = l_msg.value.split(':') #strings
                stim.stimulate(int(chnl_s), float(time_s))
            if l_msg.key == 'B':
                chnl_ls, time_ls = l_msg.value.split(':')#strings of 
                                                         #lists                 
                chnl = [int(i) for i in chnl_ls.split(',')]
                time = [float(i) for i in time_ls.split(',')]
                stim.bulk_stimulate(chnl, time)
        else:
            if os.getppid() == 1:
                return
            

class HapticStimulatorControlPeer(ConfiguredMultiplexerServer):
    '''Class to control sensory stimulation'''
    @log_crash
    def __init__(self, addresses):
        super(HapticStimulatorControlPeer, self).__init__(addresses=addresses,
                                          type=peers.HAPTICS_STIMULATOR)
        ids = self.config.get_param("id").split(":")
        vid, pid = [int(i, base=16) for i in ids]
        self.sendc, recvc = Pipe() 
        self.cproc = Process(target=controlProcess,
                             args=(vid, pid, recvc))
        self.cproc.daemon=True # subrocess should die with parrent 
                               # sadly doesn't work on SIGKILL
        self.cproc.start()
        self.ready()
        self.logger.info("HapticController init finished!")
    
    def close(self, exc_type, exc_value, traceback):
        self.cproc.terminate()
        
    def handle_message(self, mxmsg):
        '''Receives message HAPTIC_CONTROL_MESSAGE and sends it
        to stimulation board control process.
        
        Message contains info of type::
            
                message Variable {
                    required string key = 1;
                    required string value = 2;
                    }
        
        :param key: - 'S' or 'B' - Single haptic channel or
        Bulk - multiple channel to activate
        :param value: - for single channel - '1:1.0' - first channel 
        for 1 second. For bulk: '1,2:1.0,0.4' - activate channel 1 for
        1 second and channel 2 for 0.4 seconds. Channels can be in any
        order'''
            
        if mxmsg.type == types.HAPTIC_CONTROL_MESSAGE:
            l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            self.sendc.send(l_msg) #send received command to 
            #control process - threads are being locked by GIL
            #while waiting for next message
            self.logger.info('Activating haptic msg:\n{}'.format(l_msg))
        self.no_response()

if __name__ == "__main__":
    HapticStimulatorControlPeer(settings.MULTIPLEXER_ADDRESSES).loop()
    
    
