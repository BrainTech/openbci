#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import socket

from configs import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from gui import gui_logging as logger
LOGGER = logger.get_logger("ugm_server")

class UgmServer(ConfiguredMultiplexerServer):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, addresses):
        """Init server."""
        self.socket = None
        super(UgmServer, self).__init__(addresses=addresses,
                                          type=peers.UGM)

        self.ip = self.config.get_param('internal_ip')
        self.port = int(self.config.get_param('internal_port'))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.ready()


    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys update message to 
        ugm_engine using udp sockets."""
        if self.socket is None:
            self.no_response()
            return

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

