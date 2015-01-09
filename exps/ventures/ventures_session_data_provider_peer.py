#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path, time
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.acquisition.acquisition_helper import get_file_path

class SessionDataProvider(ConfiguredMultiplexerServer):

    def __init__(self, addresses):
        super(SessionDataProvider, self).__init__(addresses=addresses,
                                                type=peers.CLIENT)
        self._id = self.config.get_param('id')
        self._session_name = self.config.get_param('session_name')
        self._init_params()
        self.ready()
            
    def _init_params(self):
        save_file_name = ''.join([self._id, '_', self._session_name, '_', time.strftime('20%y-%m-%d_%H-%M-%S')])
        self.config.set_param('save_file_name', save_file_name)
    
if __name__ == "__main__":
    SessionDataProvider(settings.MULTIPLEXER_ADDRESSES).loop()
