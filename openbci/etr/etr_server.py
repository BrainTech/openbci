#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

import etr_manager

import random, time
import etr_logging as logger
LOGGER = logger.get_logger("etr_amplifier")




class EtrServer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(EtrServer, self).__init__(addresses=addresses, type=peers.ETR_SERVER)
        self.mgr = etr_manager.EtrManager()
        LOGGER.info("Wait for ugm to intialise...")
        time.sleep(3) #TODO
        ugm = self.mgr.get_initial_ugm_config()
        LOGGER.info("Sending ugm configurationmessage...")
        l_ugm_msg = variables_pb2.UgmUpdate()
        l_ugm_msg.type = 0 #TODO ?
        l_ugm_msg.value = ugm
        self.conn.send_message(
            message = l_ugm_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)


    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            LOGGER.info("GOT MESSAGE: "+str(l_msg))
            dec, ugm = self.mgr.handle_message(l_msg)
            if dec is not None:
                LOGGER.info("Sending dec message...")
                l_dec_msg = variables_pb2.Decision()
                l_dec_msg.decision = dec
                l_dec_msg.type = 0
                self.send_message(message = l_dec_msg.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)
            elif ugm is not None:
                LOGGER.info("Sending ugm message...")
                l_ugm_msg = variables_pb2.UgmUpdate()
                l_ugm_msg.type = 1 #TODO ?
                l_ugm_msg.value = ugm
                self.conn.send_message(
                    message = l_ugm_msg.SerializeToString(), 
                    type=types.UGM_UPDATE_MESSAGE, flush=True)
            else:
                LOGGER.info("Got notihing from manager...")
        self.no_response()
            


if __name__ == "__main__":
    EtrServer(settings.MULTIPLEXER_ADDRESSES).loop()
