#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

"""Current script is supposed to be fired if you want to run 
ugm as a part of openbci (with multiplexer and all that stuff)."""
import socket, time, sys

from obci.utils import tagger
from obci.utils import context as ctx
from obci.configs import variables_pb2

BUF = 2**19

class UdpServer(object):
    """The class solves a problem with PyQt - it`s main window MUST be 
    created in the main thread. As a result I just can`t fire multiplexer
    and fire ugm_engine in a separate thread because it won`t work. I can`t
    fire ugm_engine and then fire multiplexer in a separate thread as 
    then multiplexer won`t work ... To solve this i fire ugm_engine in the 
    main thread, fire multiplexer in separate PROCESS and create TcpServer
    to convey data from multiplexer to ugm_engine."""
    def __init__(self, p_ugm_engine, p_ip, p_use_tagger, context=ctx.get_dummy_context('UdpServer')):
        """Init server and store ugm engine."""
        self.context = context
        self._ugm_engine = p_ugm_engine
        self._use_tagger = p_use_tagger
        if self._use_tagger:
            self._tagger = tagger.get_tagger()

        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind((p_ip, 0))

    def run(self):
        """Do forever:
        wait for data from ugm_server (it should be UgmUpdate() message
        type by now), parse data and send it to self._ugm_engine."""
        try:
            while True:
                # Wait for data from ugm_server
                l_full_data = self.socket.recv(BUF)
                self.process_message(l_full_data)
        finally:
            self.socket.close()

    def process_message(self, message):
        # should represent UgmUpdate type...
        l_msg = variables_pb2.UgmUpdate()
        try:
            l_msg.ParseFromString(message)
            if len(l_msg.value) == 0:
                raise Exception("UgmUpdate message len is 0. Assumed parse error!!!")
            l_time = time.time()
            self._ugm_engine.queue_message(l_msg)
            self.context['logger'].debug("Got ugm update message: ")
            self.context['logger'].debug(l_msg.value)
            if self._use_tagger:
                self._tagger.send_tag(l_time, l_time, "ugm_update", 
                                      {"ugm_config":str(l_msg.value)})
        except:
            self.context['logger'].info("PARSER ERROR, too big ugm update message or not UGM_UPDATE_MESSAGE... Try UGM_CONTROL_MESSAGE")
            l_msg = variables_pb2.Variable()
            try:
                l_msg.ParseFromString(message)
                self.context['logger'].info("Properly parsed UGM_CONTROL_MESSAGE...")
                self._ugm_engine.control(l_msg)
            except:
                self.context['logger'].info("PARSER ERROR, too big ugm control message  or not UGM_CONTROL_MESSAGE... Do nothing!")
