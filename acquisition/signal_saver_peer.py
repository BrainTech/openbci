#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import sys, os.path, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings, variables_pb2
from acquisition import acquisition_logging as logger
from analysis.obci_signal_processing.signal import data_file_proxy
from analysis.obci_signal_processing.signal import signal_exceptions as  data_storage_exceptions

LOGGER = logger.get_logger("signal_saver", 'info')

DATA_FILE_EXTENSION = ".obci.raw"
class SignalSaver(ConfiguredMultiplexerServer):

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
            LOGGER.info("First sample ts:" + repr(self._first_sample_timestamp))
            LOGGER.info("First sample system ts:" + repr(time.time()))
            break

        self._data_proxy.set_data_len(len(p_data), self._samples_per_vector)

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
            from utils import streaming_debug
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')), LOGGER)


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
        self._init_saving_session()
        self.ready()
        self._session_is_active = True

    def handle_message(self, mxmsg):
        """Handle messages:
        * amplifier_signal_message - raw data from mx.
        If session is active convey data to save_manager.
        * signal_saver_finish_message - finish saving session"""

        if mxmsg.type == self._signal_type and \
                self._session_is_active:

            self._number_of_samples += self._samples_per_vector
            self._data_received(mxmsg.message)

            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()

        elif mxmsg.type == types.SIGNAL_SAVER_CONTROL_MESSAGE:
            v = variables_pb2.Variable()
            v.ParseFromString(mxmsg.message)
            if v.key == 'finish':
                LOGGER.info("Signal saver got finish saving _message.")
                LOGGER.info("Last sample ts ~ "+repr(time.time()))
                self._finish_saving_session()
            else:
                LOGGER.warning("Signal saver got unknown control message "+v.key+"!")                
        self.no_response()

    def _init_saving_session(self):
        """Start storing data..."""

        if self._session_is_active:
            LOGGER.error("Attempting to start saving signal to file while not closing previously opened file!")
            return
        append_ts = int(self.config.get_param("append_timestamps"))
        if append_ts:
            self._append_ts_index = len(self.config.get_param("channel_names").split(";"))
        else:
            self._append_ts_index = -1

        self._samples_per_vector = int(self.config.get_param("samples_per_packet"))

        l_f_name =  self.config.get_param("save_file_name")
        l_f_dir = self.config.get_param("save_file_path")
        self._number_of_samples = 0
        l_f_dir = os.path.expanduser(os.path.normpath(l_f_dir))
        if not os.access(l_f_dir, os.F_OK):
             os.mkdir(l_f_dir)
        self._file_path = os.path.normpath(os.path.join(
               l_f_dir, l_f_name + DATA_FILE_EXTENSION))

        self._data_proxy = data_file_proxy.MxBufferDataFileWriteProxy(self._file_path)

        self._signal_type = types.__dict__[self.config.get_param("signal_type")]


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

        l_files = self._data_proxy.finish_saving(self._append_ts_index)

        self.conn.send_message(
            message=l_vec.SerializeToString(),
            type=types.SIGNAL_SAVER_FINISHED, flush=True)

        LOGGER.info("Saved file "+str(l_files))
        return l_files

if __name__ == "__main__":
    SignalSaver(settings.MULTIPLEXER_ADDRESSES).loop()



