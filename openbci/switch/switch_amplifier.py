#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
from multiplexer.clients import BaseMultiplexerServer

import random, time, configurer
import switch_logging as logger

LOGGER = logger.get_logger("switch_amplifier", "info")


class SwitchAmplifier(BaseMultiplexerServer):
    def __init__(self, addresses):
        configurer_ = configurer.Configurer(addresses)
        configs = configurer_.get_configs(['SWITCH_KEY_CODE', 'SWITCH_MOUSE_BUTTON'])
        self.mouse_button = configs['SWITCH_MOUSE_BUTTON']
        self.key_code = configs['SWITCH_KEY_CODE']
        super(SwitchAmplifier, self).__init__(addresses=addresses, type=peers.SWITCH_AMPLIFIER)
        configurer_.set_configs({'PEER_READY':str(peers.SWITCH_AMPLIFIER)}, self.conn)

    def handle_message(self, mxmsg):
        if mxmsg.type == types.UGM_ENGINE_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if (l_msg.key == 'mouse_event' and l_msg.value == self.mouse_button) or \
                    (l_msg.key == 'keybord_event' and l_msg.value == self.key_code):
                LOGGER.info("Got ugm engine message: "+l_msg.key+" - "+l_msg.value+". Send switch message!")
                self.conn.send_message(message = "",
                                       type = types.SWITCH_MESSAGE, flush=True)            
            else:
                LOGGER.info("Got ugm engine message: "+l_msg.key+" - "+l_msg.value+" but not sending switch!")
        self.no_response()

if __name__ == "__main__":
    SwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).loop()

