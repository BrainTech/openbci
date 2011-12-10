#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2, configurer

import random, time
import switch_logging as logger
LOGGER = logger.get_logger("switch_server", "info")




class SwitchServer(BaseMultiplexerServer):
    def __init__(self, addresses):
        configurer_ = configurer.Configurer(addresses)
        requested_configs = ['SWITCH_RUNNING_ON_START', 'PEER_READY'+str(peers.UGM),
                             'PEER_READY'+str(peers.LOGIC)]
        LOGGER.info("Request system settings ...")
        configs = configurer_.get_configs(requested_configs)
        self.running = int(configs['SWITCH_RUNNING_ON_START'])
        self._curr_index = -1

        LOGGER.info("Got system settings, run etr_server ...")
        super(SwitchServer, self).__init__(addresses=addresses, type=peers.SWITCH_SERVER)
        configurer_.set_configs({'PEER_READY':str(peers.SWITCH_SERVER)}, self.conn)
        LOGGER.info("SwitchServer init finished!")


    def handle_message(self, mxmsg):
        if mxmsg.type == types.SWITCH_CONTROL_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'stop':
                LOGGER.info("Stop switch!")
                self.running = False
            elif l_msg.key == 'start':
                LOGGER.info("Start switch!")
                self.running = True
            else:
                LOGGER.warning("Unrecognised switch control message! "+str(l_msg.key))
        elif mxmsg.type == types.BLINK_MESSAGE:
            if self.running:
                l_msg = variables_pb2.Blink()
                l_msg.ParseFromString(mxmsg.message)
                LOGGER.info("Got blink message: "+str(l_msg.index))
                self._curr_index = int(l_msg.index)
            else:
                LOGGER.warning("Got blink message, but not running!!! Do noting.")
        elif mxmsg.type == types.SWITCH_MESSAGE:
            if self.running:
                if self._curr_index < 0:
                    LOGGER.warning("Got switch message, but curr_index < 0. Do noting!!!")
                else:
                    LOGGER.info("Got switch message, send curr index == "+str(self._curr_index))
                    l_dec_msg = variables_pb2.Decision()
                    l_dec_msg.decision = self._curr_index
                    l_dec_msg.type = 0
                    self.conn.send_message(message = l_dec_msg.SerializeToString(), 
                                           type = types.DECISION_MESSAGE, flush=True)
            else:
                LOGGER.warning("Got switch message, but not running!!! Do noting.")


        self.no_response()
            


if __name__ == "__main__":
    SwitchServer(settings.MULTIPLEXER_ADDRESSES).loop()
