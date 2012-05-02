#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from gui.ugm import ugm_helper
from configs import settings, variables_pb2
from logic import logic_logging as logger
LOGGER = logger.get_logger("logic_decision_feedback")


class LogicDecisionFeedback(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(LogicDecisionFeedback, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_FEEDBACK)

        self.feed_time = float(self.config.get_param('feed_time'))
        self.dec_count = int(self.config.get_param('dec_count'))
        self.feed_manager = ugm_helper.UgmColorUpdater(
            self.config.get_param('ugm_config'),
            [int(i) for i in self.config.get_param('ugm_field_ids').split(';')]
            )
        
        
        assert(self.feed_time >= 0)
        assert(self.dec_count > 0)
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            dec = int(mxmsg.message)
            LOGGER.info("Got decision: "+str(dec))
            assert(dec < self.dec_count)
            assert(dec >= 0)
            dec_time = time.time()
            self._send_feedback(dec, dec_time)
        self.no_response()

    def _send_feedback(self, dec, dec_time):
        while True:
            t = time.time() - dec_time
            if t > self.feed_time:
                ugm_config = self.feed_manager.update_ugm(dec, -1)
                ugm_helper.send_config(self.conn, ugm_config, 1)
                break
            else:
                LOGGER.debug("t="+str(t)+"FEED: "+str(t/self.feed_time))
                ugm_config = self.feed_manager.update_ugm(dec, 1-(t/self.feed_time))
                ugm_helper.send_config(self.conn, ugm_config, 1)
                time.sleep(0.05)

if __name__ == "__main__":
    LogicDecisionFeedback(settings.MULTIPLEXER_ADDRESSES).loop()

