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
import settings, cPickle, collections, variables_pb2, os, sys


class StreamReceiver(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(StreamReceiver, self).__init__(addresses=addresses, type=peers.STREAM_RECEIVER)
        self.channels = "1 2 3" 
        self.conn.send_message(message=self.channels, type=types.SIGNAL_STREAMER_START, flush=True)       
        print "send start"
        self.index = 0
        self.stopped = False
        #self.file = open("new_stream1", 'w')

    def handle_message(self, mxmsg):
        if mxmsg.type == types.STREAMED_SIGNAL_MESSAGE:
            self.index += 1
            print "handle ",self.index
            #file = open("new_stream", 'w')
            #if (self.index <= 2):
            #    self.file.write(mxmsg.message)
            #file.close()
            #print mxmsg.message
            vector = variables_pb2.SampleVector()
            vector.ParseFromString(mxmsg.message)
            for s in vector.samples:
                print "value ",s.value, " timestamp ",s.timestamp
            # self.index += 1
            if (self.index >= 100):  #and (self.stopped == False):
                self.conn.send_message(message=" ", type=types.SIGNAL_STREAMER_STOP, flush=True)
                #self.file.close()
                #print "DONE"
                self.stopped = True

           

if __name__ == "__main__":
    StreamReceiver(settings.MULTIPLEXER_ADDRESSES).loop()
