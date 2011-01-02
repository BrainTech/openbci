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
import settings, variables_pb2
import time
from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("P300", "debug")

import p300_engine
def sort_blinks(b1, b2):
    if b1.timestamp > b2.timestamp:
        return 1
    elif b1.timestamp < b2.timestamp:
        return -1
    else:
        return 0
class P300Analysis(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(P300Analysis, self).__init__(addresses=addresses, type=peers.ANALYSIS)

        self.channels_to_analyse = [0]
        channels_names_to_analyse = ['Cz']
        self.engine = p300_engine.P300Engine(128, channels_names_to_analyse)
        

    def handle_message(self, mxmsg):
        self.no_response()
        if mxmsg.type == types.BLINK_VECTOR_MESSAGE:
            #Get blinks to 'blinks' variable
            blinks = variables_pb2.BlinkVector()
            blinks.ParseFromString(mxmsg.message)
            blinks = list(blinks.blinks)
            blinks.sort(sort_blinks)
            LOGGER.debug("GOT BLINKS:****************")
            for b in blinks:
                LOGGER.info("ts/value: "+str((b.timestamp, b.index)))
            LOGGER.debug("***************************")

            #get all needed channels
            channels = []
            for ch_ind in self.channels_to_analyse:
                ch_samples = variables_pb2.SampleVector()
                LOGGER.debug("Start waiting for data...")
                t = time.time()
                ch_samples.ParseFromString(self.conn.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
                ch_samples = ch_samples.samples
                LOGGER.debug("Got data in time: "+str(time.time() - t))
                LOGGER.debug("Data len: "+str(len(ch_samples)))
                channels.append(ch_samples)
            decision = self.engine.get_decision(blinks, channels)
            dec = variables_pb2.Decision()
            dec.decision = decision
            dec.type = 0
            self.conn.send_message(message = dec.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)            

            
            
if __name__ == "__main__":
    P300Analysis(settings.MULTIPLEXER_ADDRESSES).loop()
