#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, time, sys, thread, socket

from multiplexer.multiplexer_constants import peers, types

from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.control.peer.configured_client import ConfiguredClient
from obci.utils.openbci_logging import log_crash
from obci.configs import settings, variables_pb2
from obci.acquisition import acquisition_helper

from obci.utils import tagger
from obci.utils import context as ctx

SOCKET_BUF = 2**19

class UdpServer(object):
    def __init__(self, engine, ip, context=ctx.get_dummy_context('UdpServer')):
        """Init server and store ugm engine."""
        self._context = context
        self._engine = engine
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, 0))

    def run(self):
        try:
            while True:
                # Wait for data from ugm_server
                full_data = self.socket.recv(SOCKET_BUF)
                self._process_message(full_data)
        finally:
            self.socket.close()

    def _process_message(self, message):
        msg = variables_pb2.IntVariable()
        try:
            msg.ParseFromString(message)
            self._engine.handle_message(msg)
        except:
            self._context['logger'].info("PARSER ERROR, too big WII ANALYSIS MESSAGE or BAD MESSAGE TYPE... Do nothing!")


class BiofeedbackOnlineLogicPeer(ConfiguredClient):
    @log_crash
    def __init__(self, addresses):
        super(BiofeedbackOnlineLogicPeer, self).__init__(addresses=addresses, type=peers.CLIENT)
        #initialise game engin for current user

        engine = a#calibration.Calibration(user_id)
        srv = UdpServer(engine, self.get_param('internal_ip'))
        self.set_param('internal_port', str(srv.socket.getsockname()[1]))
        thread.start_new_thread(srv.run, ())
        self.ready()
        engine.run()

        self.logger.info("Gui closed. Wait for finish saving..")
        acquisition_helper.finish_saving(addresses)
        self.logger.info("Finish saving ended! Exiting app ...")
        sys.exit(0)

            
if __name__ == "__main__":
    BiofeedbackOnlineLogicPeer(settings.MULTIPLEXER_ADDRESSES)
