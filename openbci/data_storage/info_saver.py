#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path
import settings, variables_pb2

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

import data_storage_logging as logger
from openbci.offline_analysis.obci_signal_processing.signal import info_file_proxy

LOGGER = logger.get_logger("info_saver", 'info')
INFO_FILE_EXTENSION = ".obci.xml"

class InfoSaver(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(InfoSaver, self).__init__(addresses=addresses, 
                                          type=peers.INFO_SAVER)
        #local params
        l_f_name = self.config.get_param("save_file_name")
        l_f_dir = self.config.get_param("save_file_path")
        l_file_path = os.path.normpath(os.path.join(
               l_f_dir, l_f_name + INFO_FILE_EXTENSION))
        self._info_proxy = info_file_proxy.InfoFileWriteProxy(l_file_path)
        self.append_ts = int(self.config.get_param("append_timestamps"))

        #external params
        self.freq = float(self.config.get_param("sampling_rate"))
        self.amp_null=float(self.config.get_param("amplifier_null"))
        self.ch_nums = self.config.get_param("channel_numbers").split(";")
        self.ch_names = self.config.get_param("channel_names").split(";")
        self.ch_gains = [float(i) for i in self.config.get_param("channel_gains").split(";")]
        self.ch_offsets = [float(i) for i in self.config.get_param("channel_offsets").split(";")]
        self.ch_as = [float(i) for i in self.config.get_param("channel_as").split(";")]
        self.ch_bs = [float(i) for i in self.config.get_param("channel_bs").split(";")]

        self.ready()

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

        l_signal_params = {
            'number_of_channels':len(self.ch_nums),
            'sampling_frequency':self.freq,
            'amplifier_null':self.amp_null,
            'channels_numbers':self.ch_nums,
            'channels_names':self.ch_names,
            'channels_gains':self.ch_gains,
            'channels_offsets':self.ch_offsets,
            'channels_as':self.ch_as,
            'channels_bs':self.ch_bs,
            'number_of_samples':p_number_of_samples,
            'file':p_data_file_path,
            'first_sample_timestamp':p_first_sample_ts
            }
        
        if self.append_ts:
            l_signal_params['number_of_channels'] += 1
            l_signal_params["channels_numbers"].append("1000")
            
            # Add name to special channel
            l_signal_params["channels_names"].append("TSS")

            # Add gain to special channel
            l_signal_params["channels_gains"].append(1.0)

            # Add offset to special channel
            l_signal_params["channels_offsets"].append(0.0)


        l_log = "Finished saving info with values:\n"
        for i_key, i_value in l_signal_params.iteritems():
            l_log = ''.join([l_log, i_key, " : ", str(i_value), "\n"])
        LOGGER.info(l_log)
        
        self._info_proxy.finish_saving(l_signal_params)

if __name__ == "__main__":
    InfoSaver(settings.MULTIPLEXER_ADDRESSES).loop()

