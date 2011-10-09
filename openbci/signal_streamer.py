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
from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("streamer", 'info')
import time
import configurer
import thread


class SignalStreamer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalStreamer, self).__init__(addresses=addresses, type=peers.SIGNAL_STREAMER)
        self.state = 0 # temporarily: 0 = nothing; 1 = transmission
        self.channels = self.conn.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")
        self.subscribers = {}
        if __debug__:
            from openbci.core import streaming_debug
            self.debug = streaming_debug.Debug(128, LOGGER)
        LOGGER.info("Create configurer ...")
        self.configurer = configurer.Configurer(addresses, "AmplifierChannelsToRecord")
        thread.start_new_thread(self.configurer.run, ())
        LOGGER.info("Configurer created ...")

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            if self.state == 1:
                for node in self.subscribers:
                    self.conn.send_message(
                        message=mxmsg.message, 
                        type=types.STREAMED_SIGNAL_MESSAGE, 
                        flush=True, to=int(node))  

            if __debug__:
                #Log module real sampling rate
                self.debug.next_sample()
                 
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
