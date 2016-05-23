#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
import random, time, sys, socket

class BiofeedbackLogicExperimentServer(ConfiguredMultiplexerServer):
    def __init__(self, addresses, p_type = peers.LOGIC_WII_BOARD):
        self._socket = None
        super(BiofeedbackLogicExperimentServer, self).__init__(addresses=addresses, type=p_type)
        self._ip = self.config.get_param('internal_ip')
        self._port = int(self.config.get_param('internal_port'))
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.ready()

    def handle_message(self, mxmsg):
        if self._socket is None:
            self.no_response()
        elif mxmsg.type == types.WII_BOARD_ANALYSIS_RESULTS:
            try:
                self._socket.sendto(mxmsg.message, (self._ip, self._port))
            except Exception, e:
                self.logger.error("An error occured while sending data to ventures logic experiment!")
                self._socket.close()
                raise(e)
            self.no_response() 

if __name__ == "__main__":
    LogicVenturesExperimentServer(settings.MULTIPLEXER_ADDRESSES).loop()
