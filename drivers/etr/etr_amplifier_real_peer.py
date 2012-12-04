#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import random, time
import socket

from obci.drivers.etr import etr_amplifier
from obci.configs import settings, variables_pb2

class EtrAmplifierReal(etr_amplifier.EtrAmplifier):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, addresses):
        super(EtrAmplifierReal, self).__init__(addresses=addresses)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.get_param('rcv_ip'),int(self.get_param('rcv_port'))))
        if len(self.get_param('send_ip')) > 0:
            self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.send_socket = None
        self.ready()

    def run(self):
        try:
            while True:
                l_data, addr = self.socket.recvfrom(1024)
                l_msg = self._get_mx_message_from_etr(l_data)
                if l_msg is not None:
                    self.process_message(l_msg)
                    if self.send_socket is not None:
                        self.send_socket.sendto(
                            l_data, 
                            (self.get_param('send_ip'),
                             int(self.get_param('send_port')))
                            )
        finally:
            self.socket.close()
            if self.send_socket is not None:
                self.send_socket.close()

    def _get_mx_message_from_etr(self, p_data):
        l_msg = variables_pb2.Sample2D()
        lst = p_data.split()

        if (len(lst) != 4):
            self.logger.info("WARNING! Received data length != 4. Message ommited.")
            return None

        if lst[0] == 'x':
            try:
                l_msg.x = float(str(lst[1]).replace(",","."))
            except:
                self.logger.info("WARNING! Error while unpacking x message. Message ommited.")                
                return None
        else:
            self.logger.info("WARNING! received key different from x. Meesage ommited.")
            return None

        if lst[2] == 'y':
            try:
                l_msg.y = float(str(lst[3]).replace(",","."))
            except:
                self.logger.info("WARNING! Error while unpacking y message. Message ommited.")
                return None
        else:
            self.logger.info("WARNING! received key different from y. Meesage ommited.")
            return None
        l_msg.timestamp = time.time()
        return l_msg
            
if __name__ == "__main__":
    EtrAmplifierReal(settings.MULTIPLEXER_ADDRESSES).run()

        
