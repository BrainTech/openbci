#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci_configs import settings, variables_pb2
import random, time, sys

from drivers import drivers_logging as logger

class SwitchAmplifier(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(SwitchAmplifier, self).__init__(addresses=addresses,
                                          type=peers.SWITCH_AMPLIFIER)
        self.mouse_button = self.config.get_param('mouse_button')
        self.key_code = self.config.get_param('key_code')
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.UGM_ENGINE_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if (l_msg.key == 'mouse_event' and l_msg.value == self.mouse_button) or \
                    (l_msg.key == 'keybord_event' and l_msg.value == self.key_code):
                self.logger.info("Got ugm engine message: "+l_msg.key+" - "+l_msg.value+". Send switch message!")
                self.conn.send_message(message = "",
                                       type = types.SWITCH_MESSAGE, flush=True)            
            else:
                self.logger.warning(''.join(["Got ugm engine message: ",
                                     l_msg.key, " - ", l_msg.value,
                                     " but not sending switch! ",
                                     "Expected key-mouse is: ", self.key_code, " - ",self.mouse_button
                                        ])
                               )
        else:
            self.logger.warning("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    SwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).loop()

