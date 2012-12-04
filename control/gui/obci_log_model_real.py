#!/usr/bin/env python
# -*- coding: utf-8 -*-
import obci_log_model
import time
import socket
import select
import json

BUF = 2**15
class RealLogModel(obci_log_model.LogModel):
    def __init__(self, srv_client):
        super(RealLogModel, self).__init__()
        self.srv_client = srv_client
        self.exp_name = ''
        self.peer_name = ''

    def next_log(self):
        try:
            #print("log model real - waiting on socket ...")
            ready = select.select([self.socket], [], [], 0.5)
            if ready[0]:
                data = self.socket.recv(BUF)  
                #print("log model real - got log!!!!!! "+str(data))
                #print("log model real - got log")
                return self._process_log(data)
            else:
                raise Exception("Socket timeout!")
        except Exception, e:
            return None, None

    def _process_log(self, data):
        try:
            d = json.loads(data)
        except Exception:
            print("Error while loading log as json....!")
            return None, None
        else:
            try:
                return d['name'], ' - '.join([str(d['asctime']), str(d['message'])])#'amplifier', data
            except Exception:
                print("Error while reading logs fields: name, asctime, message!")
                return None, None
                
    def stop_running(self):
        self.srv_client.kill_peer(self.exp_name, self.peer_name, remove_config=True) 
        super(RealLogModel, self).stop_running()

    def start_running(self, exp):
        print("log model real - start running")
        port = self._init_socket()
        self.exp_name = exp.name
        self.peer_name = 'logger_'+str(time.time())
        exp.add_peer(self.peer_name, 'control/gui/obci_log_peer.py', 
                      config_sources=None, launch_deps=None, custom_config_path=None, machine=socket.gethostname())
        exp.update_peer_param(self.peer_name, 'port', str(port))

        super(RealLogModel, self).start_running(exp)

    def connect_running(self, exp):
        print("log model real - connect running")
        port = self._init_socket()
        self.exp_name = exp.name
        self.peer_name = 'logger_'+str(time.time())
        res = self.srv_client.add_peer(exp.uuid, self.peer_name, 'control/gui/obci_log_peer.py',
                                       socket.gethostname(), param_overwrites={'port':str(port)})
        self.exp_name = exp.name
        print("log model real - Srv client status add: "+str(res))

        super(RealLogModel, self).connect_running(exp)


    def _init_socket(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', 0))
        self.socket.setblocking(0)
        s = self.socket.getsockname()[1]
        print("log model real - start socket: "+str(s))
        return s

    def post_run(self):
        print("log model real - close socket "+str(self.socket.getsockname()[1]))
        self.socket.close()

