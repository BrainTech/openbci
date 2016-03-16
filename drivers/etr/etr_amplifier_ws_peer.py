#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import time

from obci.drivers.etr import etr_amplifier
from obci.configs import settings, variables_pb2

from ws4py.client.threadedclient import WebSocketClient

class EtrWebSocketClient(WebSocketClient):
    def __init__(self, peer):
        super(EtrWebSocketClient, self).__init__()
        self.peer = peer

    def opened(self):
        print("Opened")

    def closed(self, code, reason):
        print(("Closed down", code, reason))
        self.peer.end_the_loop = True

    def received_message(self, m):
        try:
            msg = json.loads(m)
            print("x = {}, y = {}".format(m['x', m['y']))
            
            l_msg = variables_pb2.Sample2D()
            l_msg.x = float(m['x'])
            l_msg.y = float(m['y'])
            l_msg.timestamp = float(m['timestamp'])
            
            self.peer.send_message(l_msg) # TODO: fixme
        except Exception as ex:
            pass


class EtrWebSocketAmplifier(etr_amplifier.EtrAmplifier):
    def __init__(self):
        super(EtrWebSocketAmplifier, self).__init__()
        
        url = 'ws://{}:{}/ws'.format(
            str(self.config.get_param('etr_ws_server_host')),
            str(self.config.get_param('etr_ws_server_port'))
        )
        
        self.ws = EtrWebSocketClient(url)
        self.ws.daemon = False
        self.ws.connect()
        
        self.end_the_loop = False

        self.ready()

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                if self.end_the_loop:
                    break
        finally:
            ws.close()
            
if __name__ == "__main__":
    EtrWebSocketAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

