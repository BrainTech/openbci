#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
from gui.ugm import ugm_helper
import random, time, sys

from interfaces import interfaces_logging as logger

LOGGER = logger.get_logger("hci_etr", "info")


class HciEtr(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(HciEtr, self).__init__(addresses=addresses,
                                     type=peers.ETR_ANALYSIS)
    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT MESSAGE: "+str(l_msg))

            dec, ugm = self.handle_etr_message(l_msg)
            if dec >= 0:
                LOGGER.debug("Sending dec message...")
                self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
            elif ugm is not None:
                LOGGER.debug("Sending ugm message...")
                ugm_helper.send_config(self.conn, ugm, 1)
            else:
                LOGGER.info("Got notihing from manager...")
        self.no_response()

    def handle_etr_message(self, msg):
        LOGGER.error("TO BE SUBCLASSED!!!")
        return None, None
