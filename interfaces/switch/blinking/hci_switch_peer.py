#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from obci.gui.ugm import ugm_helper

import random, time, sys

class HciSwitch(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(HciSwitch, self).__init__(addresses=addresses,
                                        type=peers.SWITCH_ANALYSIS)
        self._curr_index = -1
        self._last_dec_time = time.time()
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.BLINK_MESSAGE:
            l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.logger.debug("Got blink message: "+str(l_msg.index))
            self._curr_index = int(l_msg.index)
        elif mxmsg.type == types.SWITCH_MESSAGE:
            self.config.set_param('id_start', '0')
            self.config.set_param('id_count', '4')
            self.config.set_param('ugm_type', 'single')
            ugm_helper.send_update_and_start_blinking(self.conn)
            """
        #process blinks only when hold_time passed
            if self._last_dec_time > 0:
                t = time.time() - self._last_dec_time
                if t > self.hold_after_dec:
                    self._last_dec_time = 0
                else:
                    self.no_response()
                    return

            if self._curr_index < 0:
                self.logger.warning("Got switch message, but curr_index < 0. Do nothing!!!")
            else:
                self.logger.info("Got switch message, send curr index == "+str(self._curr_index))
                self._last_dec_time = time.time()
                self.conn.send_message(message = str(self._curr_index),
                                       type = types.DECISION_MESSAGE, flush=True)"""
        else:
            self.logger.warning("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    HciSwitch(settings.MULTIPLEXER_ADDRESSES).loop()
