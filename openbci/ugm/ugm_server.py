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

import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import socket
TCP_IP = '127.0.0.1'
TCP_PORT = 5010
BUFFER_SIZE = 1024

class UgmServer(BaseMultiplexerServer):
    def __init__(self, p_addresses):
        """Init server."""
        super(UgmServer, self).__init__(addresses=p_addresses, 
                                        type=peers.UGM)
    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys decision to logic engine."""
        print("UGM GOT: ", mxmsg.type)
        if (mxmsg.type == types.UGM_UPDATE_MESSAGE):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_IP, TCP_PORT))
            self.socket.send(mxmsg.message)
            self.socket.close()
        self.no_response() 

if __name__ == "__main__":
    UgmServer(settings.MULTIPLEXER_ADDRESSES).loop()

