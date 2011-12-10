#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import settings, variables_pb2
import configurer
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import socket
import logic_speller_server
import logic_logging as logger
LOGGER = logger.get_logger("logic_speller_server")

class LogicMultipleSpellerServer(logic_speller_server.LogicSpellerServer):
    """A facade between multiplexer and logic_speller_engine."""
    def __init__(self, p_addresses):
        """Init server."""
        #self.configurer = configurer.Configurer(p_addresses)
        #self.configs = self.configurer.get_configs(['SPELLER_CONFIG', 'SPELLER_START_TEXT_ID', 'SPELLER_TEXT_ID', 'PEER_READY'+str(peers.UGM)])
        #self._init_types()

        super(LogicMultipleSpellerServer, self).__init__(p_addresses=p_addresses)

        
    def _init_types(self):
        """Create a map of protobuf types."""
        super(LogicMultipleSpellerServer, self)._init_types()
        #self._types = {'switch_mode':types.SWITCH_MODE,
        #               'ugm_update_message':types.UGM_UPDATE_MESSAGE,
        #               'dict_set_message':types.DICT_SET_MESSAGE,
        #               'dict_get_request_message': types.DICT_GET_REQUEST_MESSAGE}
        self._types.update({
                'switch_control_message': types.SWITCH_CONTROL_MESSAGE,
                'ugm_control_message': types.UGM_CONTROL_MESSAGE,
                'etr_control_message': types.ETR_CONTROL_MESSAGE
                })
