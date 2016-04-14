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
    '''
    Modification to EtrWebSocketClient, which lets to capture more data
    than x and y gaze position.
    '''
    def __init__(self, url, peer,  samples_per_packet = 4):
        super(EtrWebSocketClient, self).__init__(url,)
        self.peer = peer
        self.samples_per_packet = samples_per_packet
        self.msg_vector = variables_pb2.SampleVector()
        
    def opened(self):
        self.peer.logger.info("Opened")
        
    def closed(self, code, reason):
        self.peer.logger.info(("Closed down", code, reason))
        self.peer.end_the_loop = True
        
    def received_message(self, m):
            
        msg = json.loads(str(m))
        timestamp = float(msg['timestamp'])
        sample = self.msg_vector.samples.add()
        sample.timestamp = timestamp
        try:
            sample.channels.extend(float(msg[i]) for i in self.peer.chs)
        except KeyError as e:
            unavailable_channels_set = set(self.peer.chs).difference(
                                                         set(msg.keys())
                                                                    )
            unavailable_channels_msg = ', '.join(
                                               unavailable_channels_set
                                               ) 
            msg = '''
            
            ERROR: UNAVAILABLE CHANNELS:
            {unavailable_channels}
            
            
            Channels from tracker server JSON:
            {available_channels}
            

            You've tried to access channels:
            
            {requested_channels}
            
            
            
            '''.format(unavailable_channels = unavailable_channels_msg,
                       available_channels = ', '.join(msg.keys()),
                       requested_channels = ', '.join(self.peer.chs),
                            )

            self.peer.logger.error(msg)
            raise KeyError(unavailable_channels_msg)

        if len(self.msg_vector.samples) == self.samples_per_packet:
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
        
        if message_type == 'samplevector':
            samples_per_packet = int(self.config.get_param('samples_per_packet'))
            self.ws = EtrWebSocketClient(url, self, samples_per_packet)
            self.chs = self.get_param("channel_names").split(';')
            self.set_param('channel_gains', ';'.join(
                                        [str(1.0) for i in self.chs]))
            self.set_param('channel_offsets', ';'.join(
                                          [str(0.0) for i in self.chs]))
            self.number_of_channels = int(len(self.chs))
        else:
            msg = '''
                
                
                Unrecognised etr_amplifier peer option:
                message_type={}
                 
                 
                 
                 '''.format(message_type,)
            self.logger.error(msg)
            raise Exception(msg)
        self.ws.daemon = False
        self.ws.connect()
        
        self.end_the_loop = False

        self.ready()
        self.logger.info('EtrWebSocketAmplifier init ready')

    def process_message(self, msg):
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

