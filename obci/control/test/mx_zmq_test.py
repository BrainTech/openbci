#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
o hai
"""

from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings

from zmq_mx_test import SEND
from obci.control.common.message import send_msg, recv_msg

import zmq
import time

from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

class TestServer2(ConfiguredMultiplexerServer):

    def __init__(self, addresses):
        super(TestServer2, self).__init__(
                        addresses=addresses, type=peers.HASHTABLE)
        self.ctx = zmq.Context()

        # self.pull = self.ctx.socket(zmq.PULL)
        # self.pull.connect('tcp://*:17890')

        self.push = self.ctx.socket(zmq.PUSH)
        self.push.connect('tcp://*:16789')
        print "[mx] connected :)"
        self.queries = 0
        time.sleep(0.9)
        self.ready()


    def handle_message(self, mxmsg):
        # handle something
        if mxmsg.type == types.DICT_GET_REQUEST_MESSAGE:
            # print '*',
            self.queries += 1
            self.send_message(message=str(self.queries), to=int(mxmsg.from_),
                            type=types.DICT_GET_RESPONSE_MESSAGE, flush=True)

        send_msg(self.push, str(self.queries))
        if self.queries % 10000 == 0:
            print "[mx srv]: sent ", self.queries, "messages"

        if self.queries == SEND:
            print "[mx srv]:", SEND, "queries"
        


    # def test(self):
    #     # receive test
    #     received = 0
    #     prev = -1
    #     for i in range(SEND):
    #         msg = recv_msg(self.pull)
    #         if int(msg) == prev + 1:
    #             prev = int(msg)
    #             received += 1

    #     if received == SEND:
    #         print "[mx] OK"
    #     else:
    #         print "[mx] WUT?"


    #     for i in range(SEND):
    #         send_msg(self.push, str(i))


if __name__ == "__main__":
    srv = TestServer2(settings.MULTIPLEXER_ADDRESSES)
    srv.loop()
