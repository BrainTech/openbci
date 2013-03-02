#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2

from obci.acquisition.acquisition_helper import get_file_path

class SaveFileGenerator(ConfiguredMultiplexerServer):

    def __init__(self, addresses):
        super(SaveFileGenerator, self).__init__(addresses=addresses,
                                                type=peers.CLIENT)
        
        self.file_with_name = self.config.get_param('file_with_name')
        self.file_with_name_path = self.config.get_param('path_file_with_name')
        self.file_name_addition = self.config.get_param('additon_to_name')
        self._init_save_file_name()
        self.ready()
            
    def _init_save_file_name(self):

        save_file_name = open(get_file_path(self.file_with_name_path, self.file_with_name),'r').read()
        full_save_file_name = save_file_name + self.file_name_addition
        self.config.set_param('save_file_name', full_save_file_name)
    
if __name__ == "__main__":
    SaveFileGenerator(settings.MULTIPLEXER_ADDRESSES).loop()
