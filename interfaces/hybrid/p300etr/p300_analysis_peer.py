#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
import random, time, sys

from interfaces import interfaces_logging as logger

LOGGER = logger.get_logger("etr_analysis", "info")


class P300Analysis(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(P300Analysis, self).__init__(addresses=addresses,
                                     type=peers.P300_ANALYSIS)
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT MESSAGE: "+str(l_msg))
            #zrob cos z sygnalem

        elif mxmsg.type == types.BLINK_MESSAGE:
	    blink = variables_pb2.Blink()
            blink.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT BLINK: "+str(blink.index)+" / "+str(blink.timestamp))
            #zrob cos z blinkiem
        self.no_response()

    def _send_results(self):
        r = variables_pb2.Sample()
        t.timestamp = time.time()
        for i in range(8):
            r.channels.append(random.random())
        self.conn.send_message(message = r.SerializeToString(), type = types.P300_ANALYSIS_RESULTS, flush=True)
        


if __name__ == "__main__":
    P300Analysis(settings.MULTIPLEXER_ADDRESSES).loop()

