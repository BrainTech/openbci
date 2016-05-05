#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import thread, os

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from obci.utils import context as ctx
from obci.gui.ugm import ugm_internal_server
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm.blinking import ugm_modal_blinking_engine
from obci.gui.ugm.blinking import ugm_blinking_connection
from obci.utils.openbci_logging import log_crash

class DummyClient(object):
    def __init__(self, params):
        self.params = params
    def get_param(self, key):
        return self.params[key]

class UgmModalBlinkingEnginePeer(ConfiguredClient):
    @log_crash
    def __init__(self, addresses):
        super(UgmModalBlinkingEnginePeer, self).__init__(addresses=addresses, type=peers.UGM_ENGINE_PEER)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        connection = ugm_blinking_connection.UgmBlinkingConnection(settings.MULTIPLEXER_ADDRESSES,
                                                                   context)
                                                                   
        _modalities = self.config.get_param('modalities').split(';')
        ENG = ugm_modal_blinking_engine.UgmModalBlinkingEngine(
            ugm_config_manager.UgmConfigManager(self.config.get_param('ugm_config')),
            connection,
            context,
            _modalities)
        ENG.set_configs(DummyClient(self.config.param_values()))
        srv = ugm_internal_server.UdpServer(
            ENG, 
            self.config.get_param('internal_ip'),
            int(self.config.get_param('use_tagger')),
            context
            )
        self.set_param('internal_port', str(srv.socket.getsockname()[1]))
        thread.start_new_thread(
                srv.run, 
                ()
                )
        self.ready()
        ENG.run()
            
if __name__ == "__main__":
    UgmModalBlinkingEnginePeer(settings.MULTIPLEXER_ADDRESSES)
    #assume closing ugm should stop all other peers...
    sys.exit(1)
