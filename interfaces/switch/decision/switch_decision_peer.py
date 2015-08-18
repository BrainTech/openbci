#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class SwitchDecision(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(SwitchDecision, self).__init__(addresses=addresses,
                                        type=peers.SWITCH_ANALYSIS)
        self.dec_index = int(self.config.get_param('dec_index'))
        self.switch_type = self.config.get_param('switch_type')
        self.ready()

    def handle_message(self, mxmsg):
        if (mxmsg.type == types.SWITCH_MESSAGE) and (mxmsg.message == self.switch_type):
            self.conn.send_message(message = str(self.dec_index),
                                   type = types.DECISION_MESSAGE, flush=True)

        else:
            self.logger.debug("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    SwitchDecision(settings.MULTIPLEXER_ADDRESSES).loop()
