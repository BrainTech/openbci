#!/usr/bin/env python
# -*- coding: utf-8 -*-
import obci_log_model
import time
import socket
import select

BUF = 2**15
class RealLogModel(obci_log_model.LogModel):
    def __init__(self):
        super(RealLogModel, self).__init__()

    def next_log(self):
        try:
            print("log model - waiting on socket ...")
            ready = select.select([self.socket], [], [], 0.5)
            if ready[0]:
                data = self.socket.recv(BUF)  
                print("log model - got log!!!!!! "+str(data))
                return self._process_log(data)
            else:
                raise Exception("Socket timeout!")
        except Exception, e:
            return None, None

    def _process_log(self, data):
        return 'amplifier', data

    def start_running(self, exp):
        port = self._init_socket()
        exp.add_peer('logger', 'obci_control/gui/obci_log_peer.py', 
                      config_sources=None, launch_deps=None, custom_config_path=None, machine=None)
        #TODO - ustawic machine na local
        exp.update_peer_param('logger_mati', 'port', str(port))
        super(RealLogModel, self).start_running(exp)

    def connect_running(self, exp):
        port = self._init_socket()
        #TODO - join logger to experiment

        super(RealLogModel, self).connect_running(exp)


    def _init_socket(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', 0))
        self.socket.setblocking(0)
        return self.socket.getsockname()[1]

    def post_run(self):
        print("Close socket ")
        self.socket.close()
