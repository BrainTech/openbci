#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from logic import logic_helper
from obci_configs import settings, variables_pb2
import random, time, sys

class SwitchBackup(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(SwitchBackup, self).__init__(addresses=addresses,
                                        type=peers.SWITCH_ANALYSIS)
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SWITCH_MESSAGE:
            self.logger.info("Got switch message, transform scenario!")
            logic_helper.restart_scenario(
                self.conn, 
                self.config.get_param('new_scenario'), 
                leave_on=self.config.get_param('leave_modules').split(';'))
        else:
            self.logger.warning("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    SwitchBackup(settings.MULTIPLEXER_ADDRESSES).loop()
