#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings
import variables_pb2

import zmq

import peer_config_control
import config_message


class PeerConfigMultiplexer(BaseMultiplexerServer):

    def __init__(self, addresses, config_control):
        super(PeerConfigMultiplexer, self).__init__(addresses=addresses, type=peers.PEER_CONFIG_CONTROL)
        self.config_control = config_control
        self.id = self.config_control.peer_id


    def handle_message(self, mxmsg):

        msg = config_message.ConfigMessage()
        msg.unpack(mxmsg.message)
        print "**************** got"
        print msg
        if not self.to_me(msg):
            self.no_response()
        else:
            response = self.config_control.handle_config_message(msg)
            if response:
                self.conn.send_message(response, type=types.CONFIG_MESSAGE, flush=True)
                self.no_response()
            else:
                self.no_response()

    def send_msg(self, p_config_msg):
        self.conn.send_message(p_config_msg, type=types.CONFIG_MESSAGE, flush=True)

    def to_me(self, p_msg):
        return p_msg.receiver == self.id or p_msg.receiver == ''

    def serve_once(self):
        self.last_mxmsg, self.last_connwrap = self.conn.receive_message()
        self._BaseMultiplexerServer__handle_message()

    def request_once(self, p_req_msg):
        self.send_msg(p_msg)
        self.serve_once()




class PeerConfigZeroMQ(object):
    def __init__(self, addresses, config_control):
        self.addresses = addresses
        self.config_control = config_control
        self.id = self.config_control.peer_id
        self.zmq_ctx = zmq.Context()

    def prepare_sockets(self):
        self.rep = self.zmq_ctx.socket(zmq.REP)
        self.rep.bind(self.addresses[self.id]["rep"])

        #self.pub = self.zmq_ctx.socket(zmq.PUB)
        #self.pub.bind(self.addresses[self.id]["pub"])
        #self.sub = self.zmq_ctx.socket(zmq.SUB)

        self.req = self.zmq_ctx.socket(zmq.REQ)
        srcs = self.addresses.keys()
        srcs.remove(self.id)
        for src in srcs:
            self.req.connect(self.addresses[src]["rep"])


if __name__ == "__main__":
    PeerConfigMultiplexer(settings.MULTIPLEXER_ADDRESSES).loop()