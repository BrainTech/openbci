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
LOGGER = logger.get_logger("fast_eeg_amplifier", "info")

class FastEEGAmplifier(object):
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

        self.num_of_channels = int(self.connection.query(
                message="NumOfChannels", 
                type=types.DICT_GET_REQUEST_MESSAGE).message)


        sampleVector = variables_pb2.SampleVector()
        for x in range(self.num_of_channels):
                samp = sampleVector.samples.add()
                samp.value = float(x)
                samp.timestamp = time.time()

        self.msg1 = sampleVector.SerializeToString()

        sampleVector = variables_pb2.SampleVector()
        for x in range(self.num_of_channels):
                samp = sampleVector.samples.add()
                samp.value = float(x*-1)
                samp.timestamp = time.time()
        self.msg2 = sampleVector.SerializeToString()

        self.num_of_samples = 0
        self.msg_type = 0

    def do_sampling(self):
        """Start flooding multiplexer with data..."""
        if __debug__:
            from openbci.core import streaming_debug
            self.debug = streaming_debug.Debug(self.sampling_rate, LOGGER)

        brek = 1/float(self.sampling_rate)
        real_start_time = time.time()
        data_start_time = real_start_time

        LOGGER.info("Start samples sampling.")
        while True:
            self.num_of_samples += 1
            if self.num_of_samples % int(self.sampling_rate) == 0:
                self.msg_type = (self.msg_type + 1) % 2

            t = data_start_time + (time.time() - real_start_time)
            if self.msg_type == 0:
                msg = self.msg1
            else:
                msg = self.msg2
            self.connection.send_message(
                message=msg,
                type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()

            time_to_sleep = brek - (time.time() - t) - 0.14/self.sampling_rate
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)



