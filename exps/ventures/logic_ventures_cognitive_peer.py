#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2

from obci.exps.ventures.maze_game import maze
from obci.acquisition import acquisition_helper

class LogicVenturesCognitive(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(LogicVenturesCognitive, self).__init__(addresses=addresses,
                                                     type=peers.CLIENT)
        self.ready()

        user_id = self.get_param('user_id')
        self.logger.info("Starting cognitive maze for user: "+str(user_id))

        tag_name = self.get_param('save_file_name')
        tag_dir = acquisition_helper.get_file_path(self.get_param('save_file_path'), '')
        session_name = self.get_param('session_name')
        session_type = 'experiment' if session_name == 'ventures_game' else 'training'
        maze.MazeGame(user_id, tag_dir=tag_dir, tag_name=tag_name, session_type=session_type).run()
        sys.exit(0)
    
if __name__ == "__main__":
    LogicVenturesCognitive(settings.MULTIPLEXER_ADDRESSES).loop()
