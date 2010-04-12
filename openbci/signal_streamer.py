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

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2


class SignalStreamer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalStreamer, self).__init__(addresses=addresses, type=peers.SIGNAL_STREAMER)
        self.state = 0 # temporarily: 0 = nothing; 1 = transmission
        self.channels = self.conn.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")
        self.subscribers = {}

    def handle_message(self, mxmsg):
        if mxmsg.type == types.FILTERED_SIGNAL_MESSAGE:
#            print("GOOOOOOOOOOOOOOOOOOOOOOOOOOT")
            if self.state == 1:
                for node in self.subscribers:
#                    print("2222222222222222")
                    #print "self.subscribers[node] ", self.subscribers[node]
                    #channels = self.subscribers[node].split(" ")
                    sampVec = variables_pb2.SampleVector()
                    sampVec.ParseFromString(mxmsg.message)
                    newVec = variables_pb2.SampleVector()
                    for i in self.channels:
#                        print("333333333333333333333#")
                        samp = newVec.samples.add()
                        samp.CopyFrom(sampVec.samples[int(i)])
                    self.conn.send_message(message=newVec.SerializeToString(), type=types.STREAMED_SIGNAL_MESSAGE, flush=True, to=int(node))  
                 
        elif mxmsg.type == types.SIGNAL_STREAMER_START:
            self.subscribers[str(mxmsg.from_)] = mxmsg.message
            print "channels: ", mxmsg.message
            self.state = 1
            self.no_response()
        elif mxmsg.type == types.SIGNAL_STREAMER_STOP:
           
            if str(mxmsg.from_) in self.subscribers:
                del self.subscribers[str(mxmsg.from_)]

            #self.state = 0
            self.no_response()
            


if __name__ == "__main__":
    SignalStreamer(settings.MULTIPLEXER_ADDRESSES).loop()
