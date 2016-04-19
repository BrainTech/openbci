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
#      Marian Dovgialo <marian.dowgialo@gmail.com>

from obci.configs import settings
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import variables_pb2
from obci.utils.openbci_logging import log_crash
import numpy as np
import time
import random
import sys
from scipy.signal import gaussian
import json
from threading import Thread
import pickle

AMPLITUDE=20

class SyntheticGenerator(ConfiguredMultiplexerServer):
    '''Peer to send synthetic blinks and signals, and receive
        P300 decisions to make some statistics'''
    @log_crash
    def __init__(self, addresses):
        super(SyntheticGenerator, self).__init__(addresses=addresses,
                                                type=peers.LOGIC_FEEDBACK)
                                                
        self.synthetic = int(self.config.get_param('synthetic'))
        if self.synthetic==0:
            self.targets = np.load(self.config.get_param('targets_path'))
            self.nontargets = np.load(self.config.get_param('nontargets_path'))
            self.channels_names, self.sampling_rate, self.baseline, channel_gains = self.load_meta()
            self.set_param('channel_gains', ';'.join(channel_gains))
            
        else:
            self.channels_names = self.config.get_param('channel_names').split(';')
            self.sampling_rate = float(self.config.get_param('sampling_rate'))
            self.set_param('channel_gains', ';'.join(
                                        [str(1.0) for i in self.channels_names]))
        self.set_param('channel_offsets', ';'.join(
                                      [str(0.0) for i in self.channels_names]))
            
        self.learning = int(self.config.get_param('learning'))
        self.samples_per_packet = int(self.config.get_param('samples_per_packet'))
        self.window = float(self.config.get_param('window'))
        self.noise_level = float(self.config.get_param('noise_level'))
        self.fields_s = self.config.get_param('fields').split(';')
        self.fields = [int(i) for i in self.fields_s]
        #inter stimulus interval seconds
        self.isi = float(self.config.get_param('isi'))
        #selected field
        if self.learning:
            self.focus = int(self.config.get_param('learning_target_field'))
        else:
            self.focus = self.fields[0]
        #seconds
        self.time = time.time()
        #timestamp of last blink
        self.time_of_blink=0
        self.decisions = []
        self.sent_targets=0
        self.test_trials_n = int(self.config.get_param('test_trials_n'))
        self.delay = float(self.config.get_param('delay'))
        self.statistics_path = self.config.get_param('statistics_path')
        self.command_thread = Thread(target=self.run)
        self.command_thread.start()
        
        
        self.logger.info('Init done')
        self.ready()
    
    def load_meta(self):
        with open(self.config.get_param('meta_path')) as datafile:
            meta = json.load(datafile)
        return meta['channels_names'], meta['sampling_rate'], meta['baseline'], meta['channel_gains']
        
        
    def send_nontarget_blink(self,):
        self.logger.info('sending distractor blink')
        choice = random.choice(tuple(set(self.fields)-set([self.focus])))
        b = variables_pb2.Blink()
        timestamp = self.time
        self.time_of_blink=timestamp
        b.timestamp=timestamp
        b.index=choice
        self.conn.send_message(message = b.SerializeToString(), 
                               type = types.BLINK_MESSAGE, flush=True)
                               
    def send_target_blink(self, timestamp=None):
        self.logger.info('sending target blink')
        b = variables_pb2.Blink()
        if not timestamp:
            timestamp=self.time
        self.time_of_blink=timestamp
        b.timestamp=timestamp
        b.index=self.focus
        self.conn.send_message(message = b.SerializeToString(), 
                               type = types.BLINK_MESSAGE, flush=True)
        
    def send_isi(self):
        '''send empty signal'''
        #send blink on "distractor" field
        self.send_nontarget_blink()
        packets = int((self.isi*self.sampling_rate)/self.samples_per_packet)
        length = int(packets*self.samples_per_packet)
        if self.synthetic==1:
            signal=np.random.normal(scale=self.noise_level,
                                  size=(length, len(self.channels_names)))
        else:
            selected_nontarget = random.randint(0, self.nontargets.shape[0]-1)
            #nontargets are cut to isi
            start=int(-self.baseline*self.sampling_rate)
            end = start+length
            signal = self.nontargets[selected_nontarget, :, start:end]
        for p in xrange(packets):
            sv = variables_pb2.SampleVector()
            for sn in xrange(self.samples_per_packet):
                s = sv.samples.add()
                ind = p*self.samples_per_packet+sn
                s.channels.extend(signal[:,ind].tolist())
                s.timestamp = self.time
                self.time+=1.0/self.sampling_rate
            time.sleep(self.samples_per_packet*1.0/self.sampling_rate)
            self.conn.send_message(message = sv.SerializeToString(), 
                               type = types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            
    
            
    def send_target(self):
        self.logger.info('Sending target, focus: {}'.format(self.focus))
        self.sent_targets+=1
        length_window = int(self.window*self.sampling_rate)
        length_packet_aligned = length_window - length_window % self.samples_per_packet
        gauss_w = gaussian(length_packet_aligned, length_packet_aligned/10)
        chnl_n = len(self.channels_names)
        
        
        if self.synthetic:
            signal = np.empty((chnl_n, length_packet_aligned), dtype=float)
            for nr in xrange(chnl_n):
                #first channel will have biggest amplitude, last smallest
                noise = np.random.normal(scale=self.noise_level,
                                              size=length_packet_aligned)
                signal[nr] = AMPLITUDE*gauss_w*((chnl_n*1.0-nr)/chnl_n)+noise
                self.send_target_blink()
        else:
            selected_target = random.randint(0, self.targets.shape[0]-1)
            signal = self.targets[selected_target]
            self.send_target_blink(self.time-self.baseline)
            
        
        
        for i in xrange(length_packet_aligned/self.samples_per_packet):
            sv = variables_pb2.SampleVector()
            for sn in xrange(self.samples_per_packet):
                s = sv.samples.add()
                s.channels.extend(signal[:,i*self.samples_per_packet+sn].tolist())
                s.timestamp = self.time
                self.time+=1.0/self.sampling_rate
            time.sleep(self.samples_per_packet*1.0/self.sampling_rate)
            self.conn.send_message(message = sv.SerializeToString(), 
                               type = types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            if (self.time-self.time_of_blink)>self.isi:
                self.send_nontarget_blink()
        
        
    @log_crash
    def run(self):
        time.sleep(self.delay)
        for i in xrange(self.test_trials_n):
            for k in xrange(len(self.fields)-1):
                self.send_isi()
            self.send_target()
        self.save_statistics()
        sys.exit(0)
    
    def save_statistics(self):
        
        self.logger.info('saving statistics')
        with open(self.statistics_path, 'w') as f:
            json.dump(self.decisions, f)
        self.logger.info('saving statistics - done: {}'.format(self.statistics_path))
        
    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            self.logger.info('Got message: {}'.format(mxmsg.message))
            
            decision = int(mxmsg.message)
            self.decisions.append({'sent_targets':self.sent_targets,
                                   'focus':self.focus,
                                   'got_decision':decision
                                    }
                                   )
            self.logger.info('got decision: {}'.format(self.decisions[-1]))
            self.sent_targets = 0
            if self.learning == 0:
                self.focus=random.choice(self.fields)

            

if __name__=='__main__':
    SyntheticGenerator(settings.MULTIPLEXER_ADDRESSES).loop()
