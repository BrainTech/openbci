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
from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("P300")

class P300Analysis(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(P300Analysis, self).__init__(addresses=addresses, type=peers.ANALYSIS)

    def handle_message(self, mxmsg):
        if mxmsg.type == types.BLINK_MESSAGE:
            blink = variables_pb2.Blink()
            blink.ParseFromString(mxmsg.message)
            LOGGER.info("GOT BLINK MESSSAGE: "+str(blink.index))
        self.no_response()
            
if __name__ == "__main__":
    P300Analysis(settings.MULTIPLEXER_ADDRESSES).loop()
