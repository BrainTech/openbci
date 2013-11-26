#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.logic import logic_helper
from obci.acquisition import acquisition_helper
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

import random, time, sys

class SwitchBackup(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(SwitchBackup, self).__init__(addresses=addresses,
                                        type=peers.SWITCH_ANALYSIS)
        self.time = time.time()
        self.ready()

    def handle_message(self, mxmsg):
        if (mxmsg.type == types.SWITCH_MESSAGE  and time.time() - self.time > 5):
            self.time = time.time()
            self.logger.info("Got switch message, transform scenario!")
            if int(self.config.get_param('finish_saving')):
                self.logger.info("But first send finish saving ...")
                acquisition_helper.send_finish_saving(self.conn)
            time.sleep(3)
            logic_helper.restart_scenario(
                self.conn, 
                self.config.get_param('new_scenario'), 
                leave_on=self.config.get_param('leave_modules').split(';'))
        else:
            self.logger.debug("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    SwitchBackup(settings.MULTIPLEXER_ADDRESSES).loop()
