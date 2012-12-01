#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path, time
import sys

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.analysis.obci_signal_processing.signal import info_file_proxy

INFO_FILE_EXTENSION = ".obci.xml"

class InfoSaver(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(InfoSaver, self).__init__(addresses=addresses,
                                          type=peers.INFO_SAVER)

        #local params
        l_f_name = self.config.get_param("save_file_name")
        l_f_dir = self.config.get_param("save_file_path")
        self._file_path = os.path.expanduser(os.path.normpath(os.path.join(
               l_f_dir, l_f_name + INFO_FILE_EXTENSION)))
        self._info_proxy = info_file_proxy.InfoFileWriteProxy(self._file_path)
        self.append_ts = int(self.config.get_param("append_timestamps"))

        #external params
        self.freq = float(self.config.get_param("sampling_rate"))
        self.sample_type = self.config.get_param("sample_type")
        self.ch_nums = self.config.get_param("active_channels").split(";")
        self.ch_names = self.config.get_param("channel_names").split(";")
        self.ch_gains = [float(i) for i in self.config.get_param("channel_gains").split(";")]
        self.ch_offsets = [float(i) for i in self.config.get_param("channel_offsets").split(";")]

        self.ready()

    def handle_message(self, mxmsg):
        """Handle messages:
        * signal_saver_control_message - a message from signal saver
        being a signal to finish saving."""
        if mxmsg.type == types.SIGNAL_SAVER_FINISHED:
            self.logger.info("Got signal saver finished!")
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
            time.sleep(3)
            sys.exit(0)

    def _finish_saving(self, p_number_of_samples, p_data_file_path, p_first_sample_ts):
        """Create xml manifest file with data received from hashtable
        and from signal saver (parameters in the function)."""

        l_signal_params = {
            'number_of_channels':len(self.ch_nums),
            'sampling_frequency':self.freq,
            'sample_type':self.sample_type,
            'channels_numbers':self.ch_nums,
            'channels_names':self.ch_names,
            'channels_gains':self.ch_gains,
            'channels_offsets':self.ch_offsets,
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
        self.logger.info(l_log)

        self._info_proxy.finish_saving(l_signal_params)
        l_msg = self._serialise_finished_msg(l_signal_params)

        self.conn.send_message(
            message=l_msg,
            type=types.INFO_SAVER_FINISHED, flush=True)

    def _serialise_finished_msg(self, params):
        l_dict = {
            'number_of_channels':str(params['number_of_channels']),
            'sampling_frequency':str(params['sampling_frequency']),
            'channels_numbers':';'.join([str(i) for i in params['channels_numbers']]),
            'channels_names':';'.join(params['channels_names']),
            'channels_gains':';'.join([str(i) for i in params['channels_gains']]),
            'channels_offsets':';'.join([str(i) for i in params['channels_offsets']]),
            'number_of_samples':str(params['number_of_samples']),
            'file':str(params['file']),
            'first_sample_timestamp':str(params['first_sample_timestamp']),
            #'file_path':self._file_path
            }
        l_vec = variables_pb2.VariableVector()
        for k, v in l_dict.iteritems():
            l_var = l_vec.variables.add()
            l_var.key = k
            l_var.value = v
        return l_vec.SerializeToString()

if __name__ == "__main__":
    InfoSaver(settings.MULTIPLEXER_ADDRESSES).loop()

