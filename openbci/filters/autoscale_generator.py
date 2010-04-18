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
import settings
import variables_pb2
import sys

class AutoscaleGenerator(BaseMultiplexerServer):
    """The class is mx server that receives FILTERED SAMPLES.
    Regarding gain taken from hashtable it sets offset to hashtable
    so that samples for every channel are rescaled to be close to 0.
    For given channel its offset is set to -avg_from_few_first_samples.
    """
    def __init__(self, addresses):
        """Init server, get Gain from hashtable."""
        super(AutoscaleGenerator, self).__init__(addresses=addresses, 
                                                 type=peers.AUTOSCALE_GENERATOR)
        self.channels = None
        gains = self.conn.query(
                message="Gain", 
                type=types.DICT_GET_REQUEST_MESSAGE).message
        self.gains = [float(i) for i in gains.split(' ')]
        
    def determine_scale(self):
        """The method is fired after every new samples are received.
        If we have remembered appropriate number of samples, compute
        averages, send appropriate offsets to hashtable and finish current 
        script."""
        if len(self.channels[0]) > 1000:
            avgs = []
            for i, channel in enumerate(self.channels):
                # Let`s take second 500 samples not first - to be sure
                # that some first outlayers will not be considered
                avg = self.gains[i]*sum(channel[500:])/len(channel[500:])
                # We need averages of samples multiplied by gains...
                avgs.append(avg)
            to_send = ' '.join([str(-i) for i in avgs])
            l_var = variables_pb2.Variable()
            l_var.key = "Offset"
            l_var.value = to_send
            self.conn.send_message(message =l_var,
                                   type = types.DICT_SET_MESSAGE, flush=True)
            sys.exit(0)
            
    def handle_message(self, mxmsg):
        """
        Get filtered samples, remeber few first samples, do the job, finish."""
        if mxmsg.type == types.FILTERED_SIGNAL_MESSAGE:
	    vec = variables_pb2.SampleVector()
	    vec.ParseFromString(mxmsg.message)
            if not self.channels:
                self.channels = []
                for sample in vec.samples:
                    self.channels.append([sample.value])
            else:
                for i, sample in enumerate(vec.samples):
                    self.channels[i].append(sample.value)
                self.determine_scale()
            self.no_response()


if __name__ == "__main__":
    AutoscaleGenerator(settings.MULTIPLEXER_ADDRESSES).loop()
