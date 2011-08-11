#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import socket
#IP = '127.0.0.1'
IP = '192.168.0.7'
PORT = 20320


BUFFER_SIZE = 1024
VIRTUAL = True
VIRTUAL_MANUAL = False
VIRTUAL_CONSTANT = None #0.1

import random, time


import etr_logging as logger
LOGGER = logger.get_logger("etr_amplifier")




class EtrAmplifier(object):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, p_addresses):

        # Get from hash: ETR_IP, ETR_PORT
        LOGGER.info("Start initializin etr amplifier...")
        self.connection = connect_client(type = peers.ETR_AMPLIFIER, addresses=p_addresses)
        LOGGER.info("Etr connected!")

        if not VIRTUAL:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((IP,PORT))

        LOGGER.info("Socket binded!")

    def _get_mx_message_from_etr(self, p_data):
        l_msg = variables_pb2.Sample2D()
        lst = p_data.split()

        assert(len(lst) == 4)
        if lst[0] == 'x':
            l_msg.x = float(str(lst[1]).replace(",","."))
        else:
            print "ERROR x"
        if lst[2] == 'y':
            l_msg.y = float(str(lst[3]).replace(",","."))
        else:
            print "ERROR y"
        l_msg.timestamp = time.time()
        return l_msg

    def run(self):
        """Method fired by multiplexer. It conveys update message to 
        ugm_engine using udp sockets."""
        while True:
            # Wait for data from ugm_server
            LOGGER.info("Waiting on socket ...")
            if not VIRTUAL:
                l_data, addr = self.socket.recvfrom(1024)
                l_msg = self._get_mx_message_from_etr(l_data)
            else:
                l_msg = variables_pb2.Sample2D()
                if VIRTUAL_MANUAL:
                    i = raw_input().split(' ')
                    l_msg.x = float(i[0])
                    l_msg.y = float(i[1])
                    l_msg.timestamp = time.time()
                else:
                    time.sleep(0.02)
                    if VIRTUAL_CONSTANT is not None:
                        l_msg.x = VIRTUAL_CONSTANT
                        l_msg.y = VIRTUAL_CONSTANT
                    else:
                        l_msg.x = random.random()
                        l_msg.y = random.random()
                    l_msg.timestamp = time.time()
                
                # d should represent UgmUpdate type...
            LOGGER.info("ETR sending message ... x = "+str(l_msg.x) + ", y = "+str(l_msg.y))
            self.connection.send_message(message = l_msg.SerializeToString(), type = types.ETR_SIGNAL_MESSAGE, flush=True)            
        if not VIRTUAL:
            self.socket.close()

if __name__ == "__main__":
    EtrAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

