#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
from azouk._allinone import OperationFailed, OperationTimedOut
import settings

import zmq

import peer_config_control
import common.config_message as config_message

RECV_RETRIES=5
RECV_TIMEOUT=10


class PeerConfigMx(object):

    def __init__(self, addresses, config_control):
        self.addresses = addresses
        self.conn = connect_client(type = peers.PEER_CONFIG_CONTROL, addresses=addresses)
        self.config_control = config_control
        self.id = self.config_control.peer_id
        self._recv_retry=RECV_RETRIES

    def handle_message(self, mxmsg):
        msg = config_message.ConfigMessage()
        print "**************** got {0}".format(mxmsg.type)
        print mxmsg
        if mxmsg.type == types.CONFIG_MESSAGE:
            msg.unpack(mxmsg.message)
        if self.from_me(msg) or mxmsg.type != types.CONFIG_MESSAGE:
            if self._recv_retry:
                self._recv_retry -= 1
                print "     RETRYING"
                self.serve_once()
            else:
                self._recv_retry=RECV_RETRIES
        else:
            print "-----"
            response = self.config_control.handle_config_message(msg)
            print "resp......"
            if response:
                self.conn.send_message(response, type=types.CONFIG_MESSAGE, flush=True)


    def send_msg(self, p_config_msg):
        self.conn.send_message(p_config_msg, type=types.CONFIG_MESSAGE, flush=True)

    def to_me(self, p_msg):
        return p_msg.receiver == self.id or p_msg.receiver == ''

    def from_me(self, p_msg):
        return p_msg.sender == self.id

    def serve_once(self):
        if not self.conn:
            self.conn = connect_client(type = peers.PEER_CONFIG_CONTROL,
                                        addresses=self.addresses)
        try:
            last_mxmsg, last_connwrap = self.conn.receive_message(timeout=RECV_TIMEOUT)
        except OperationTimedOut:
            print "Operation Timed ouT"
            return
        except OperationFailed:
            print "Operation Failed!"
            return

        self.handle_message(last_mxmsg)

    def request_once(self, p_req_msg):
        if not self.conn:
            self.conn = connect_client(type = peers.PEER_CONFIG_CONTROL,
                                        addresses=self.addresses)
        self.send_msg(p_req_msg)
        self.serve_once()

    def shutdown(self):
        self.conn.shutdown()
        self.conn = None




# class PeerConfigZeroMQ(object):
#     def __init__(self, addresses, config_control):
#         self.addresses = addresses
#         self.config_control = config_control
#         self.id = self.config_control.peer_id
#         self.zmq_ctx = zmq.Context()

#     def prepare_sockets(self):
#         self.rep = self.zmq_ctx.socket(zmq.REP)
#         self.rep.bind(self.addresses[self.id]["rep"])

#         #self.pub = self.zmq_ctx.socket(zmq.PUB)
#         #self.pub.bind(self.addresses[self.id]["pub"])
#         #self.sub = self.zmq_ctx.socket(zmq.SUB)

#         self.req = self.zmq_ctx.socket(zmq.REQ)
#         srcs = self.addresses.keys()
#         srcs.remove(self.id)
#         for src in srcs:
#             self.req.connect(self.addresses[src]["rep"])


if __name__ == "__main__":
    PeerConfigMultiplexer(settings.MULTIPLEXER_ADDRESSES).loop()