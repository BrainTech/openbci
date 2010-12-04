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

#import signalml_save_manager
import sys, time, os.path
import settings, variables_pb2

import data_storage_logging as logger
from tags import tagger
import svarog_file_proxy

LOGGER = logger.get_logger("info_saver", 'info')
TAGGER = tagger.get_tagger()

#TIMESTAMPS_AS_SEPARATE_CHANNEL = False
SVAROG_INFO_FILE_EXTENSION = ".obci.svarog.info"
class InfoSaver(BaseMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(InfoSaver, self).__init__(addresses=addresses, 
                                          type=peers.INFO_SAVER)

        l_f_name =  self.conn.query(message = "SaveFileName", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message
        l_f_dir = self.conn.query(message = "SaveFilePath", 
                                   type = types.DICT_GET_REQUEST_MESSAGE, 
                                   timeout = 1).message
        l_file_path = os.path.normpath(os.path.join(
               l_f_dir, l_f_name + SVAROG_INFO_FILE_EXTENSION))
        self._info_proxy = svarog_file_proxy.SvarogFileWriteProxy(l_file_path)

    def handle_message(self, mxmsg):
        """Handle messages:
        * signal_saver_control_message - a message from signal saver
        being a signal to finish saving."""
        if mxmsg.type == types.SIGNAL_SAVER_CONTROL_MESSAGE:
            LOGGER.info("Got signal saver control message!")
            l_vec = variables_pb2.VariableVector()
            l_vec.ParseFromString(mxmsg.message)
            l_num_of_samples = None
            l_file_path = None
            for i_var in l_vec.variables:
                if i_var.key == 'number_of_samples':
                    l_num_of_samples = i_var.value
                elif i_var.key == 'file_path':
                    l_file_path = i_var.value
                elif i_var.key == 'first_sample_timestamp':
                    l_first_sample_ts = i_var.value
            self._finish_saving(l_num_of_samples, l_file_path, l_first_sample_ts)

    def _finish_saving(self, p_number_of_samples, p_data_file_path, p_first_sample_ts):
        """Create xml manifest file with data received from hashtable
        and from signal saver (parameters in the function)."""

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
        l_append_ts = int(self.conn.query(message = "SaverTimestampsIndex", 
                                          type = types.DICT_GET_REQUEST_MESSAGE, 
                                          timeout = 1).message)


        l_signal_params['number_of_channels'] = len(l_ch_nums)
        l_signal_params['sampling_frequency'] = l_freq
        l_signal_params['channels_numbers'] = l_ch_nums
        l_signal_params['channels_names'] = l_ch_names
        l_signal_params['channels_gains'] = l_ch_gains
        l_signal_params['channels_offsets'] = l_ch_offsets
        l_signal_params['number_of_samples'] = p_number_of_samples
        l_signal_params['file'] = p_data_file_path
        l_signal_params['first_sample_timestamp'] = p_first_sample_ts
        
        if l_append_ts > -1:
            l_signal_params['number_of_channels'] += 1
            l_signal_params["channels_numbers"].insert(l_append_ts, "1000")
            
            # Add name to special channel
            l_signal_params["channels_names"].insert(l_append_ts, "TIMESTAMPS")

            # Add gain to special channel
            l_signal_params["channels_gains"].insert(l_append_ts, "1.0")

            # Add offset to special channel
            l_signal_params["channels_offsets"].insert(l_append_ts, "0.0")


        l_log = "Finished saving info with values:\n"
        for i_key, i_value in l_signal_params.iteritems():
            l_log = ''.join([l_log, i_key, " : ", str(i_value), "\n"])
        LOGGER.info(l_log)

        
        self._info_proxy.finish_saving(l_signal_params)
        


if __name__ == "__main__":
    InfoSaver(settings.MULTIPLEXER_ADDRESSES).loop()

