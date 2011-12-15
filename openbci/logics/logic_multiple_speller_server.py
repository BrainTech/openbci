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
        super(LogicMultipleSpellerServer, self).__init__(p_addresses=p_addresses)

        
    def _init_types(self):
        """Create a map of protobuf types."""
        super(LogicMultipleSpellerServer, self)._init_types()
        self._types.update({
                'switch_control_message': types.SWITCH_CONTROL_MESSAGE,
                'ugm_control_message': types.UGM_CONTROL_MESSAGE,
                'etr_control_message': types.ETR_CONTROL_MESSAGE,
                'ssvep_control_message': types.SSVEP_CONTROL_MESSAGE,
                })
