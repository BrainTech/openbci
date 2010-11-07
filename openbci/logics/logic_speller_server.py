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
import socket

import logic_logging as logger
LOGGER = logger.get_logger("logic_speller_server")

class LogicSpellerServer(BaseMultiplexerServer):
    """A facade between multiplexer and logic_speller_engine."""
    def __init__(self, p_addresses):
        """Init server."""
        super(LogicSpellerServer, self).__init__(addresses=p_addresses, 
                                                 type=peers.LOGIC)
        self._init_types()
        
    def _init_types(self):
        """Create a map of protobuf types."""
        self._types = {'switch_mode':types.SWITCH_MODE,
                       'ugm_update_message':types.UGM_UPDATE_MESSAGE,
                       'dict_set_message':types.DICT_SET_MESSAGE,
                       'dict_get_request_message': types.DICT_GET_REQUEST_MESSAGE}
    def _get_type(self, p_type):
        """For given string p_type return protobuf type."""
        return self._types[p_type]

    def set_engine(self, p_engine):
        """Setter for logic_engine slot."""
        self._logic_engine = p_engine
	self._logic_engine._update_global_gui()
    def send_message(self, p_params):
        """Method fired by logic_engine. It sends p_params data."""
        LOGGER.info("Speller server will send message type: "+p_params['type'])
        LOGGER.debug("Speller server will send message type: "+str(p_params))
        l_message = ''
        if p_params.get('key','') != '': #dictionary message
            l_msg_var = variables_pb2.Variable()
            l_msg_var.key = p_params['key']
            l_msg_var.value = p_params['value']
            l_message = l_msg_var.SerializeToString()
        elif p_params['type'] == 'ugm_update_message':
            l_msg_var = variables_pb2.UgmUpdate()
            l_msg_var.type = 1 #'simple' update type 
            l_msg_var.value = p_params['value']
            l_message = l_msg_var.SerializeToString()
        else:
            l_message = p_params['value']


        self.conn.send_message(message = l_message, 
                               type = self._get_type(p_params['type']), 
                               flush = True)
    def _update_igui(self, decision):
        UDP_IP="127.0.0.1"
        UDP_PORT=4002
        MESSAGES = {"0":"First Stimuli 401", "1":"Second Stimulu 402", "2":"Third Stimuli 403", "4":"Fourth Stimuli 404"}
        MESSAGE=MESSAGES[decision]

        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "message:", MESSAGE
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM ) # UDP
        sock.sendto( MESSAGE, (UDP_IP, UDP_PORT) )
 
    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys decision to logic engine."""
	print "received message"
        if (mxmsg.type == types.DECISION_MESSAGE):
            dec = variables_pb2.Decision()
            dec.ParseFromString(mxmsg.message)
	    print "decision message"
	    #self._update_igui(str(dec.decision))
            self._logic_engine.handle_decision(dec)
        self.no_response() 


if __name__ == "__main__":
    print("The script is not supposed to be fired as a program!")
 
