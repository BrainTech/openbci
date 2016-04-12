#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import time

from obci.drivers.etr import etr_amplifier
from obci.configs import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types

from ws4py.client.threadedclient import WebSocketClient

class EtrWebSocketClient(WebSocketClient):
    def __init__(self, url, peer):
        '''
        :param url: Url to websocket wich provides data
        :param peer: EtrWebSocketAmplifier peer'''
        super(EtrWebSocketClient, self).__init__(url)
        self.peer = peer

    def opened(self):
        self.peer.logger.info("Opened")

    def closed(self, code, reason):
        self.peer.logger.info(("Closed down", code, reason))
        self.peer.end_the_loop = True

    def received_message(self, m):
    
        msg = json.loads(str(m))
        self.peer.logger.info("msg: {}".format(m))
        l_msg = variables_pb2.Sample2D()
        l_msg.x = float(msg['x'])
        l_msg.y = float(msg['y'])
        l_msg.timestamp = float(msg['timestamp'])
        
        self.peer.process_message(l_msg)

class EtrWebSocketClientSample(EtrWebSocketClient):
    '''
    Modification to EtrWebSocketClient, which lets to capture more data
    than x and y gaze position.
    '''
    def __init__(self, url, peer,  packet = 4):
        super(EtrWebSocketClientSample, self).__init__(url, peer,)
        
        self.packetsize = packet
        self.msg_vector = variables_pb2.SampleVector()
    def received_message(self, m):
            
        msg = json.loads(str(m))
        #~ self.peer.logger.info("msg: {}".format(m))
        timestamp = float(msg['timestamp'])
        sample = self.msg_vector.samples.add()
        sample.timestamp = timestamp
        
        sample.channels.extend(
            [float(msg['{}'.format(i)]) for i in self.peer.chs]
            )
        if len(self.msg_vector.samples) == self.packetsize:
            #send when big enough and create new empty vector
            self.peer.process_message(self.msg_vector)
            self.msg_vector = variables_pb2.SampleVector()
        
class EtrWebSocketAmplifier(etr_amplifier.EtrAmplifier):
    def __init__(self, addresses):
        super(EtrWebSocketAmplifier, self).__init__(addresses)
        url = 'ws://{}:{}/ws'.format(
            str(self.config.get_param('etr_ws_server_host')),
            str(self.config.get_param('etr_ws_server_port'))
        )
        message_type = str(self.config.get_param('message_type'))
        if message_type=='sample2d':
            self.ws = EtrWebSocketClient(url, self)
        elif message_type == 'samplevector':
            packetsize = int(self.config.get_param('samples_per_packet'))
            self.ws = EtrWebSocketClientSample(url, self, packetsize)
            self.chs = self.get_param("channel_names").split(';')
            self.set_param('channel_gains', ';'.join(
                                        [str(1.0) for i in self.chs]))
            self.set_param('channel_offsets', ';'.join(
                                          [str(0.0) for i in self.chs]))
            self.number_of_channels = int(len(self.chs))
        else:
            raise(Exception('Unrecognised option: message_type'))
            
            
        self.ws.daemon = False
        self.ws.connect()
        
        self.end_the_loop = False

        self.ready()

    def process_message(self, msg):
        #~ self.logger.debug("ETR WS sending message = "+str(msg))
        self.conn.send_message(message = msg.SerializeToString(), 
                               type = types.TOBII_SIGNAL_MESSAGE, flush=True)

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                if self.end_the_loop:
                    break
        finally:
            self.ws.close()
            
if __name__ == "__main__":
    EtrWebSocketAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

