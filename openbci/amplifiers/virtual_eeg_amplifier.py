#!/usr/bin/env python
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
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

"""This module provides an abstract class for virtual amplifiers that 
performs standard actions.
It should be subclassed by concrete virtual amplifiers (eg. file, function).
__int__ method should be subclass, where .sampling_rate and .channel_numbers
should be defined and set."""

import time
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import amplifiers_logging as logger
from openbci.data_storage import signalml_read_manager
from openbci.data_storage import data_storage_exceptions
LOGGER = logger.get_logger("virtual_eeg_amplifier")

class VirtualEEGAmplifier(object):
    """An abstract class for virtual amplifiers that performs standar actions.
    It should be subclassed by concrete virtual amplifiers (eg. file, function).
    __int__ method should be subclass, where .sampling_rate and .channel_numbers
    should be defined and set."""
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        # We need to get basic configuration from hashtable as
        # other modules will expect the same configuration..

        # sampling rate
        self.sampling_rate = int(self.connection.query(
                message="SamplingRate", 
                type=types.DICT_GET_REQUEST_MESSAGE).message)

        # determine number of channels
        # channel_numbers_string will be sth like: "0 1 2 3"
        channel_numbers_string = self.connection.query(
                message="AmplifierChannelsToRecord", 
                type=types.DICT_GET_REQUEST_MESSAGE).message

        self.num_of_channels = len(channel_numbers_string.split(" "))

    def do_sampling(self):
        """Start flooding multiplexer with data..."""
        if __debug__:
            from openbci.core import streaming_debug
            self.debug = streaming_debug.Debug(128, LOGGER)

        offset = 0.0
        brek = 1/float(self.sampling_rate)
        real_start_time = time.time()
        data_start_time = real_start_time #self._get_sampling_start_time()
        channels_data = [0]*len(self.channel_numbers)
        channels_data_len = len(channels_data)
        while True:
            try:
                for i in range(channels_data_len):
                    channels_data[i] = self._get_next_value(offset)
                                   
            except data_storage_exceptions.NoNextValue:
                LOGGER.info("All samples has been red. Sampling finished.")
                break
            offset += 1.0
            sampleVector = variables_pb2.SampleVector()
            # For real-time data: t = time.time() = real_start_time + (time.time() - real_start_time)
            # For historical-time data: t = data_start_time + (time.time() - real_start_time)
            # But for real-time data: real_start_time == data_start_time, so:
            t = data_start_time + (time.time() - real_start_time)
            for x in channels_data:
                samp = sampleVector.samples.add()
                samp.value = float(x)
                samp.timestamp = t
            self.connection.send_message(
                message=sampleVector.SerializeToString(), 
                type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)

            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()
            time_to_sleep = brek - (time.time() - t)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)
    def _get_sampling_start_time(self):
        raise Exception("VirtualEEGAmplifier is an abstract class.\
Method get_sampling_start_time should be reimplemented in subclass.")



