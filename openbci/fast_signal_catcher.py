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
#
import time

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2
from openbci.core import core_logging as logger
LOGGER = logger.get_logger("signal_catcher", "debug")


class SignalCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalCatcher, self).__init__(addresses=addresses, type=peers.SIGNAL_CATCHER)
        self.number_of_channels = len(self.conn.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" "))
        self.buffer_size = int(self.conn.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.buffer = [collections.deque() for z in range(self.number_of_channels)]
        self.return_vector = variables_pb2.SampleVector()
        for i in range(self.buffer_size):
            s = self.return_vector.samples.add()
            s.value = 0.0
            s.timestamp = 0.0

        if __debug__:
            from openbci.core import streaming_debug
            sampling = int(self.conn.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
            self.debug = streaming_debug.Debug(sampling, LOGGER)
            self.prev = -1

    def add(self, value):
        sampleVector = variables_pb2.SampleVector()
        sampleVector.ParseFromString(value)
        values = sampleVector.samples

        #for x in values:
        #    print "sc ", float(x.timestamp)
        #    print "sc val ", float(x.value)
        #print "SC: ",values[0].timestamp
        #print "SC val: ",values[0].value
        # buffer[i] = buffer_size samples from channel i
        i = 0
        for s in values:
            #LOGGER.debug("GOT SAMPLE: "+str(s.value))
            if s.value - 1 != self.prev:
                LOGGER.error("ERROR, a sample was lost, should be: "+str(self.prev + 1)+" got: "+str(s.value))
            self.prev = s.value
            self.buffer[i].append(s)
            if len(self.buffer[i]) > self.buffer_size:
                self.buffer[i].popleft()
            i += 1

        

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_CATCHER_REQUEST_MESSAGE:
            ind = int(mxmsg.message)
            t = time.time()
            for i in range(self.buffer_size):
                try:
                    self.return_vector.samples[i].value = self.buffer[ind][i].value
                    self.return_vector.samples[i].timestamp = self.buffer[ind][i].timestamp
                except IndexError:
                    self.return_vector.samples[i].value = 0.0
                    self.return_vector.samples[i].timestamp = 0.0

            LOGGER.debug("Updated vector in time: "+str(time.time() - t))
            t = time.time()
            m = self.return_vector.SerializeToString()
            LOGGER.debug("Serialize vector in time: "+str(time.time() - t))

            self.send_message(message = m, type = types.SIGNAL_CATCHER_RESPONSE_MESSAGE)

        elif mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            self.add(mxmsg.message)
            self.no_response()
            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()



if __name__ == "__main__":
    SignalCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
