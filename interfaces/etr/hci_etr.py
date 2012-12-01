#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.gui.ugm import ugm_helper
import random, time, sys

class HciEtr(ConfiguredMultiplexerServer):
    def __init__(self, addresses, p_type = peers.ETR_ANALYSIS):
        super(HciEtr, self).__init__(addresses=addresses,
                                    type=p_type)

    def handle_message(self, mxmsg):
        
        if mxmsg.type == types.ETR_CALIBRATION_RESULTS:

            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            data = res.channels
            self.logger.debug("GOT ETR CALIBRATION RESULTS: "+str(data))
            
            self.handle_calibration_mesage(data)
            
        elif mxmsg.type == types.ETR_SIGNAL_MESSAGE:
            l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            self.logger.debug("GOT MESSAGE: "+str(l_msg))

            dec, ugm = self.handle_etr_message(l_msg)
            if dec >= 0:
                self.logger.debug("Sending dec message...")
                self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
            elif ugm is not None:
                self.logger.debug("Sending ugm message...")
                ugm_helper.send_config(self.conn, ugm, 1)
            else:
                self.logger.info("Got notihing from manager...")

        self.no_response()

    def handle_etr_message(self, msg):
        self.logger.error("TO BE SUBCLASSED!!!")
        return None, None

    def handle_calibration_mesage(self, msg):
        self.logger.error("TO BE SUBCLASSED!!!")
        return None 
