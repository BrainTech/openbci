#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import thread, os

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from configs import settings, variables_pb2
from drivers import drivers_logging as logger
from gui.ugm import ugm_internal_server
from gui.ugm import ugm_config_manager
from gui.ugm.blinking import ugm_blinking_engine
from gui.ugm.blinking import ugm_blinking_connection

class DummyClient(object):
    def __init__(self, params):
        self.params = params
    def get_param(self, key):
        return self.params[key]

class UgmBlinkingEnginePeer(ConfiguredClient):
    def __init__(self, addresses):
        super(UgmBlinkingEnginePeer, self).__init__(addresses=addresses, type=peers.UGM_ENGINE_PEER)
        connection = ugm_blinking_connection.UgmBlinkingConnection(settings.MULTIPLEXER_ADDRESSES)
        ENG = ugm_blinking_engine.UgmBlinkingEngine(
            ugm_config_manager.UgmConfigManager(self.config.get_param('ugm_config')),
            connection)
        ENG.set_configs(DummyClient(self.config.param_values()))
        thread.start_new_thread(
                ugm_internal_server.UdpServer(
                    ENG, 
                    self.config.get_param('internal_ip'),
                    int(self.config.get_param('internal_port')),
                    int(self.config.get_param('use_tagger'))
                    ).run, 
                ()
                )
        self.ready()
        ENG.run()
            
if __name__ == "__main__":
    UgmBlinkingEnginePeer(settings.MULTIPLEXER_ADDRESSES).run()
