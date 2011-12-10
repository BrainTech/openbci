#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2, configurer

import etr_manager
from nesw import etr_nesw_manager

import random, time
import etr_logging as logger
LOGGER = logger.get_logger("etr_amplifier", "info")




class EtrServer(BaseMultiplexerServer):
    def __init__(self, addresses):
        configurer_ = configurer.Configurer(addresses)
        configs = configurer_.get_configs(['ETR_TYPE','ETR_RUNNING_ON_START'])
        self.running = int(configs['ETR_RUNNING_ON_START'])
        if configs['ETR_TYPE'] == 'CLASSIC':
            self.mgr = etr_manager.EtrManager()
        elif configs['ETR_TYPE'] == 'NESW':
            self.mgr = etr_nesw_manager.EtrNeswManager()            

        requested_configs = self.mgr.get_requested_configs()
        requested_configs.add('PEER_READY'+str(peers.UGM))
        requested_configs.add('PEER_READY'+str(peers.LOGIC))
        requested_configs.add('PEER_READY'+str(peers.ETR_AMPLIFIER))

        LOGGER.info("Request system settings ...")
        configs = configurer_.get_configs(requested_configs)
        self.mgr.set_configs(configs)

        LOGGER.info("Got system settings, run etr_server ...")
        super(EtrServer, self).__init__(addresses=addresses, type=peers.ETR_SERVER)
        configurer_.set_configs({'PEER_READY':str(peers.ETR_SERVER)}, self.conn)
        LOGGER.info("EtrServer init finished!")

    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_CONTROL_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'stop':
                LOGGER.info("Stop etr!")
                self.running = False
            elif l_msg.key == 'start':
                LOGGER.info("Start etr!")
                self.running = True
            else:
                LOGGER.warning("Unrecognised etr control message! "+str(l_msg.key))

        if mxmsg.type == types.ETR_SIGNAL_MESSAGE:
            if self.running:
                l_msg = variables_pb2.Sample2D()
                l_msg.ParseFromString(mxmsg.message)
                LOGGER.debug("GOT MESSAGE: "+str(l_msg))
                
                dec, ugm = self.mgr.handle_message(l_msg)
                if dec >= 0:
                    LOGGER.info("Sending dec message...")
                    l_dec_msg = variables_pb2.Decision()
                    l_dec_msg.decision = dec
                    l_dec_msg.type = 0
                    self.conn.send_message(message = l_dec_msg.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)
                elif ugm is not None:
                    LOGGER.info("Sending ugm message...")
                    l_ugm_msg = variables_pb2.UgmUpdate()
                    l_ugm_msg.type = 1
                    l_ugm_msg.value = ugm
                    self.conn.send_message(
                        message = l_ugm_msg.SerializeToString(), 
                        type=types.UGM_UPDATE_MESSAGE, flush=True)
                else:
                    LOGGER.info("Got notihing from manager...")


        self.no_response()
            


if __name__ == "__main__":
    EtrServer(settings.MULTIPLEXER_ADDRESSES).loop()
