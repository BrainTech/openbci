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

"""This module should be fired as script so that UGM_UPDATE_MESSAGE
is received and send by tcp to ugm_engine"""
import settings
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import socket

import configurer
import ugm_logging as logger
LOGGER = logger.get_logger("ugm_server")

class UgmServer(BaseMultiplexerServer):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, p_addresses):
        """Init server."""
        cfg = configurer.Configurer(settings.MULTIPLEXER_ADDRESSES)
        configs = cfg.get_configs(['UGM_INTERNAL_IP', 'UGM_INTERNAL_PORT'])
        self.ip = configs['UGM_INTERNAL_IP']
        self.port = int(configs['UGM_INTERNAL_PORT'])
        super(UgmServer, self).__init__(addresses=p_addresses, 
                                        type=peers.UGM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cfg.set_configs({'PEER_READY':str(peers.UGM)}, self.conn)


    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys update message to 
        ugm_engine using udp sockets."""

        if (mxmsg.type == types.UGM_UPDATE_MESSAGE or mxmsg.type == types.UGM_CONTROL_MESSAGE):
            try:
                self.socket.sendto(mxmsg.message, (self.ip, self.port))
            except Exception, l_exc:
                LOGGER.error("An error occured while sending data to ugm_engine")
                self.socket.close()
                raise(l_exc)
        self.no_response() 

if __name__ == "__main__":
    UgmServer(settings.MULTIPLEXER_ADDRESSES).loop()

