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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

"""This module provides a dummy, the simplest possible virtual amplifier. For dev. purposes.
It gets number of channels from hashtable and stream random data to MX every 0.0005 second
(In practice +/1 128HZ)"""

import time, random
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import amplifiers_logging as logger

LOGGER = logger.get_logger("dummy_amplifier")

class DummyAmplifier(object):
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        time.sleep(1)
        # Below we need to determine basic configuration from hashtable
        # becouse other modules will expect the same configuration

        # determine number of channels
        # channel_numbers_string will be sth like: "0 1 2 3"
        channel_numbers_string = self.connection.query(
                message="AmplifierChannelsToRecord", 
                type=types.DICT_GET_REQUEST_MESSAGE).message

        self.num_of_channels = len(channel_numbers_string.split(" "))

    def do_sampling(self):
        """Start flooding multiplexer with data..."""
        samplesVector = variables_pb2.SampleVector()
        for i in range(self.num_of_channels):
            samp = samplesVector.samples.add()

        while True:
            # Determine random vector of data
            t = time.time()
            for i in range(self.num_of_channels):
                samplesVector.samples[i].value = random.random()
                samplesVector.samples[i].timestamp = t

            self.connection.send_message(
                message=samplesVector.SerializeToString(), 
                type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            time.sleep(0.0005)

if __name__ == "__main__":
    DummyAmplifier().do_sampling()



