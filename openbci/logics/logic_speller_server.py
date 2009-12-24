#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

class LogicSpellerServer(BaseMultiplexerServer):
    """A facade between multiplexer and logic_speller_engine."""
    def __init__(self, p_addresses):
        """Init server."""
        super(LogicSpellerServer, self).__init__(addresses=p_addresses, 
                                                 type=peers.LOGIC)
        self._init_types()
        self._message_var = variables_pb2.Variable()
    def _init_types(self):
        """Create a map of protobuf types."""
        self._types = {'switch_mode':types.SWITCH_MODE,
                       'dict_set_message':types.DICT_SET_MESSAGE,
                       'dict_get_request_message': types.DICT_GET_REQUEST_MESSAGE}
    def _get_type(self, p_type):
        """For given string p_type return protobuf type."""
        return self._types[p_type]

    def set_engine(self, p_engine):
        """Setter for logic_engine slot."""
        self._logic_engine = p_engine

    def send_message(self, p_params):
        """Method fired by logic_engine. It sends p_params data."""
        l_message = ''
        if p_params.get('key','') == '':
            l_message = p_params['value']
        else:
            self._message_var.key = p_params['key']
            self._message_var.value = p_params['value']
            l_message = self._message_var.SerializeToString()
        self.conn.send_message(message = l_message, 
                               type = self._get_type(p_params['type']), 
                               flush = True)
        
    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys decision to logic engine."""
        if (mxmsg.type == types.DECISION_MESSAGE):
            dec = variables_pb2.Decision()
            dec.ParseFromString(mxmsg.message)
            self._logic_engine.handle_decision(dec)
        self.no_response() 


if __name__ == "__main__":
    print("The script is not supposed to be fired as a program!")
 
