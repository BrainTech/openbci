#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import thread, os

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from configs import settings, variables_pb2
from drivers import drivers_logging as logger
from gui.ugm import ugm_engine
from gui.ugm import ugm_internal_server
from gui.ugm import ugm_config_manager

class UgmEnginePeer(ConfiguredClient):
    def __init__(self, addresses):
        super(UgmEnginePeer, self).__init__(addresses=addresses, type=peers.UGM_ENGINE_PEER)

        ENG = ugm_engine.UgmEngine(
            ugm_config_manager.UgmConfigManager(self.config.get_param('ugm_config')))
        srv = ugm_internal_server.UdpServer(
            ENG, 
            self.get_param('internal_ip'),
            int(self.get_param('use_tagger'))
            )
        self.set_param('internal_port', str(srv.socket.getsockname()[1]))
        thread.start_new_thread(
                srv.run, 
                ()
                )
        self.ready()
        ENG.run()
            
if __name__ == "__main__":
    UgmEnginePeer(settings.MULTIPLEXER_ADDRESSES)
    #assume closing ugm should stop all other peers...
    sys.exit(1)


