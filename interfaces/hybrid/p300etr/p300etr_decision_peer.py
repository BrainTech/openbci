#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
import random, time, sys

from interfaces import interfaces_logging as logger

LOGGER = logger.get_logger("p300_etr_decision", "debug")


class P300EtrDecision(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(P300EtrDecision, self).__init__(addresses=addresses,
                                     type=peers.RESULTS_ANALYSIS)
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_ANALYSIS_RESULTS:
	    res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT ETR ANALYSIS RESULTS: "+str(res.channels))

            #self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
        elif mxmsg.type == types.P300_ANALYSIS_RESULTS:
	    res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT P300 ANALYSIS RESULTS: "+str(res.channels))

            #self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

        self.no_response()

if __name__ == "__main__":
    P300EtrDecision(settings.MULTIPLEXER_ADDRESSES).loop()
