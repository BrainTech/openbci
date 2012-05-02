#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from configs import settings, variables_pb2

from multiplexer.clients import BaseMultiplexerServer
from zmq_mx_test import SEND
from common.message import send_msg, recv_msg

import zmq
import time

from peer.configured_client import ConfiguredClient
from multiplexer.clients import connect_client
import common.config_message as cmsg
from azouk._allinone import OperationFailed, OperationTimedOut

class TestClient2(ConfiguredClient):

    def __init__(self, addresses):
        super(TestClient2, self).__init__(addresses=addresses, type=peers.CONFIGURER)
        # self.conn = connect_client(addresses=addresses, type=peers.CONFIGURER)
        self.ready()
        print "[mx client] connected :)"



    def test(self):
        
        req = cmsg.fill_msg(types.GET_CONFIG_PARAMS,
                            sender='aaa',
                            param_names=['a'],
                            receiver='')
        received = 0
        for i in range(SEND):
            msg = self.__query(self.conn, req, types.DICT_GET_REQUEST_MESSAGE)
            if msg is None:
                print ":((("
                continue


            if int(msg.message) == received + 1:
                received += 1
            if received % 10000 == 0:
                print "made ", received, "queries"

        if received == SEND:
            print "[mx peer...] OK"
        else:
            print "[mx peer...] WUT?", received

        self.set_param('ach', '567')


    def __query(self, conn, msg, msgtype):
        try:
            reply = conn.query(message=msg,
                                    type=msgtype)
        except OperationFailed:
            print '[', 'client', "] Could not connect to config server"
            reply = None
        except OperationTimedOut:
            print '[', 'client', "] Operation timed out! (could not connect to config server)"
            reply = None
        return reply


if __name__ == "__main__":
    srv = TestClient2(settings.MULTIPLEXER_ADDRESSES)
    srv.test()