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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>


from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

import signalml_save_manager
import sys, time
import settings, variables_pb2

import data_storage_logging as logger
from tags import tagger

LOGGER = logger.get_logger("signal_saver", 'info')
TAGGER = tagger.get_tagger()

TIMESTAMPS_AS_SEPARATE_CHANNEL = False

class SignalSaver(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalSaver, self).__init__(addresses=addresses, 
                                          type=peers.SIGNAL_SAVER)
        self._session_is_active = False
        self._save_manager = None
        if __debug__:
            from openbci.core import streaming_debug
            self.debug = streaming_debug.Debug(128, LOGGER)

        self.start_saving_session()

    def handle_message(self, mxmsg):
        """Handle messages:
        * amplifier_signal_message - raw data from mx.
        If session is active convey data to save_manager.
        * signal_saver_control_message - start or finish saving session
        depending on data received."""
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE and \
                self._session_is_active:
            l_vec = variables_pb2.SampleVector()
            l_vec.ParseFromString(mxmsg.message)
	    for i_sample in l_vec.samples:
                ts = i_sample.timestamp
                self._save_manager.data_received(i_sample.value, ts)
                
            if TIMESTAMPS_AS_SEPARATE_CHANNEL:
                self._save_manager.data_received(ts, ts)
            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()

        elif mxmsg.type == types.SIGNAL_SAVER_CONTROL_MESSAGE:
            LOGGER.info("Signal saver got signal_saver_control_message: "+\
                            mxmsg.message)
            if mxmsg.message == 'finish_saving':
                self.finish_saving_session()
            elif mxmsg.message == 'start_saving':
                self.start_saving_session()
        elif mxmsg.type == types.TAG and \
                self._session_is_active:
            #TODO - decide which type of tag is to be saved
            l_tag = TAGGER.unpack_tag(mxmsg.message)
            LOGGER.info(''.join(['Signal saver got tag: ',
                                'start_timestamp:',
                                str(l_tag['start_timestamp']),
                                ', end_timestamp: ', 
                                str(l_tag['end_timestamp']),
                                ', name: ',
                                l_tag['name'],
                                '. <Change debug level to see desc.>']))
                                  
            LOGGER.debug("Signal saver got tag: "+str(l_tag))
            self._save_manager.tag_received(l_tag)
  
                
    def start_saving_session(self):
        if self._session_is_active:
            LOGGER.error("Attempting to start saving signal to file while not closing previously opened file!")
            return 
        self._session_is_active = True
        l_signal_params = {}
        l_freq = int(self.conn.query(message = "SamplingRate", 
                                     type = types.DICT_GET_REQUEST_MESSAGE, 
                                     timeout = 1).message)
        l_ch_nums = self.conn.query(message = "AmplifierChannelsToRecord", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message.strip().split(' ')
        l_ch_names = self.conn.query(message = "ChannelsNames", 
                                     type = types.DICT_GET_REQUEST_MESSAGE, 
                                     timeout = 1).message.strip().split(';')
        l_ch_gains = self.conn.query(message = "Gain", 
                                     type = types.DICT_GET_REQUEST_MESSAGE, 
                                     timeout = 1).message.strip().split(' ')
        l_ch_offsets = self.conn.query(message = "Offset", 
                                       type = types.DICT_GET_REQUEST_MESSAGE, 
                                       timeout = 1).message.strip().split(' ')
        l_f_name =  self.conn.query(message = "SaveFileName", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message
        l_f_path = self.conn.query(message = "SaveFilePath", 
                                   type = types.DICT_GET_REQUEST_MESSAGE, 
                                   timeout = 1).message

        l_signal_params['number_of_channels'] = len(l_ch_nums)
        l_signal_params['sampling_frequency'] = l_freq
        l_signal_params['channels_numbers'] = l_ch_nums
        l_signal_params['channels_names'] = l_ch_names
        l_signal_params['channels_gains'] = l_ch_gains
        l_signal_params['channels_offsets'] = l_ch_offsets
        if TIMESTAMPS_AS_SEPARATE_CHANNEL:
            l_signal_params['number_of_channels'] += 1
            l_signal_params['channels_gains'].append(1.0)
            l_signal_params['channels_offsets'].append(0.0)
            l_signal_params['channels_names'].append('TIMESTAMPS')
            l_signal_params['channels_numbers'].append(1000)

        l_log = "Start saving to file "+l_f_path+l_f_name+" with values:\n"
        for i_key, i_value in l_signal_params.iteritems():
            l_log = ''.join([l_log, i_key, " : ", str(i_value), "\n"])
        LOGGER.info(l_log)

        self._save_manager = signalml_save_manager.SignalmlSaveManager(
           l_f_name, l_f_path, l_signal_params)

    def finish_saving_session(self):
        if not self._session_is_active:
            LOGGER.error("Attempting to stop saving signal to file while no file being opened!")
            return
        self._session_is_active = False
        l_files = self._save_manager.finish_saving()

        LOGGER.info("Saved files: \n"+str(l_files))
        return l_files

if __name__ == "__main__":
    SignalSaver(settings.MULTIPLEXER_ADDRESSES).loop()


        
