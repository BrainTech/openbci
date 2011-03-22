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

import data_file_proxy
import sys, time, os.path
import settings, variables_pb2

import data_storage_logging as logger
import data_storage_exceptions
from tags import tagger

LOGGER = logger.get_logger("signal_saver", 'info')
TAGGER = tagger.get_tagger()
DATA_FILE_EXTENSION = ".obci.dat"
class SignalSaver(BaseMultiplexerServer):

    def _all_but_first_data_received(self, p_data):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy.
        _all_but_first_data_received is set to self.data_received in 
        self._first_sample_data_received, so in fact _all_but_first_data_received
        is fired externally by calling self.data_received."""
        try:
            self._data_proxy.data_received(p_data)
        except data_storage_exceptions.BadSampleFormat, e:
            LOGGER.error("Received sample is not of a good size. Writing aborted!")
            sys.exit(1)


    def _first_sample_data_received(self, p_data):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy.
        first_sample_data_received is set to self.data_received in self.__init__, so in fact
        first_sample_data_received is fired externally by calling self.data_received"""

        # Set some additional first_sample-like data

        msg = p_data
        l_vec = variables_pb2.SampleVector()
        l_vec.ParseFromString(msg)
        for i_sample in l_vec.samples:
            self._first_sample_timestamp = i_sample.timestamp
            break

        self._data_proxy.set_data_len(len(p_data))
        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!! below operation changes self._data_received method 
        # from _first_sample_timestamp to _all_but_first_data_received
        self._data_received = self._all_but_first_data_received
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self._data_received(p_data)


    def __init__(self, addresses):
        super(SignalSaver, self).__init__(addresses=addresses, 
                                          type=peers.SIGNAL_SAVER)
        if __debug__:
            from openbci.core import streaming_debug
            self.debug = streaming_debug.Debug(128, LOGGER)


        self._session_is_active = False

        # A method fired ever time we get new samples
        # We need to do something when got first sample
        # so for efficency reasons we do that kind of python hack...
        # self._data_received is again changed im method
        # self._first_sample_data_received
        self._data_received = self._first_sample_data_received

        # Needed slots
        self._number_of_samples = 0
        self._first_sample_timestamp = -1.0

        self._start_saving_session()

    def handle_message(self, mxmsg):
        """Handle messages:
        * amplifier_signal_message - raw data from mx.
        If session is active convey data to save_manager.
        * signal_saver_finish_message - finish saving session"""

        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE and \
                self._session_is_active:

            self._number_of_samples += 1
            self._data_received(mxmsg.message)

            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()

        elif mxmsg.type == types.SIGNAL_SAVER_FINISH_SAVING:
            LOGGER.info("Signal saver got finish saving _message")
            self._finish_saving_session()
                
    def _start_saving_session(self):
        """Start storing data..."""
        if self._session_is_active:
            LOGGER.error("Attempting to start saving signal to file while not closing previously opened file!")
            return 

        l_f_name =  self.conn.query(message = "SaveFileName", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message
        l_f_dir = self.conn.query(message = "SaveFilePath", 
                                   type = types.DICT_GET_REQUEST_MESSAGE, 
                                   timeout = 1).message
        self._append_ts = int(self.conn.query(message = "SaverTimestampsIndex", 
                                          type = types.DICT_GET_REQUEST_MESSAGE, 
                                          timeout = 1).message)

        l_f_dir = os.path.normpath(l_f_dir)
        if not os.access(l_f_dir, os.F_OK):
             os.mkdir(l_f_dir)
        self._file_path = os.path.normpath(os.path.join(
               l_f_dir, l_f_name + DATA_FILE_EXTENSION))

        self._data_proxy = data_file_proxy.MxBufferDataFileWriteProxy(self._file_path)
        self._session_is_active = True

    def _finish_saving_session(self):
        """Send signal_saver_control_message to MX with
        number of samples and first sample timestamp (for tag_saver and info_saver).
        Also perform .finish_saving on data_proxy - it might be a long operation..."""
        if not self._session_is_active:
            LOGGER.error("Attempting to stop saving signal to file while no file being opened!")
            return
        self._session_is_active = False

        l_vec = variables_pb2.VariableVector()

        l_var = l_vec.variables.add()
        l_var.key = 'first_sample_timestamp'
        l_var.value = repr(self._first_sample_timestamp)

        l_var = l_vec.variables.add()
        l_var.key = 'number_of_samples'
        l_var.value = str(self._number_of_samples)

        l_var = l_vec.variables.add()
        l_var.key = 'file_path'
        l_var.value = self._file_path

        self.conn.send_message(
            message=l_vec.SerializeToString(), 
            type=types.SIGNAL_SAVER_CONTROL_MESSAGE, flush=True)
        
        l_files = self._data_proxy.finish_saving(self._append_ts)
        LOGGER.info("Saved file "+str(l_files))
        return l_files




if __name__ == "__main__":
    SignalSaver(settings.MULTIPLEXER_ADDRESSES).loop()


        
