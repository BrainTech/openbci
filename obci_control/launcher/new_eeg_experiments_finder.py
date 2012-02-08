#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import time
import sys
import threading

from launcher.obci_client import OBCIClient
import common.net_tools as net
from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes
from launcher.launcher_tools import obci_root

class NewEEGExperimentFinder(object):
    def __init__(self, srv_addrs, ctx):
        self.client = OBCIClient(srv_addrs, ctx)#client_server_prep()
        self.poller = PollingObject()
        self.mtool = OBCIMessageTool(message_templates)
        self._amplified_cache = {}

    def launch_discovery(self):
        result = self.client.send_create_experiment(
                                        launch_file=obci_root() + '/scenarios/run_driver_discovery.ini', 
                                        name='automatic_eeg_discovery')
        
        if result.type != 'experiment_created':
            print "Discovery experiment creation fail!", result
            return result, None
        
        exp_data = result
        print "experiment created", exp_data

        exp_sock = self.client.ctx.socket(zmq.REQ)
        for addr in exp_data.rep_addrs:
            exp_sock.connect(addr)

        send_msg(exp_sock, self.mtool.fill_msg("start_experiment"))
        result, details =  self.poll_recv(exp_sock, 20000)

        if result.type != 'starting_experiment':
            print "Discovery experiment start fail!", result
        print "experiment launching", result
        return exp_data, exp_sock

    def monitor_launching(self, exp_data):
        exp_sock = self.client.ctx.socket(zmq.SUB)
        for addr in exp_data.pub_addrs:
            print addr
            exp_sock.connect(addr)
        exp_sock.setsockopt(zmq.SUBSCRIBE, "")
        while True:
            message = recv_msg(exp_sock)
            msg = self.mtool.unpack_msg(message)
            print msg

    def wait_for_discovery_registration(self, exp_data):
        exp_sock = self.client.ctx.socket(zmq.SUB)
        for addr in exp_data.pub_addrs:
            print addr
            exp_sock.connect(addr)
        exp_sock.setsockopt(zmq.SUBSCRIBE, "")

        discov_params = None
        while discov_params is None:
            message = recv_msg(exp_sock)
            msg = self.mtool.unpack_msg(message)
            if msg.type == 'obci_control_message' and \
                    msg.msg_code == 'obci_peer_registered' and msg.launcher_message:
                if msg.launcher_message['peer_id'] == 'driver_discovery':
                    discov_params = msg.launcher_message['params']

        return discov_params

    def request_available_drivers(self, exp_sock):
        send_msg(exp_sock, self.mtool.fill_msg('get_peer_param_values', 
                                                peer_id='driver_discovery'))
    
    def receive_available_drivers(self, exp_sock):
        result, details = self.poll_recv(exp_sock, 4000)
        if not result:
            print "Connection timed out...", details
            return None, result 

        if result.type != 'peer_param_values':
            print "Peer info error: ", result
            return None, result

        driver_info = result.param_values['available_drivers']
        if driver_info == '':
            print "Try again later"
        return driver_info, result

    def poll_recv(self, socket, timeout):
        result, details = self.poller.poll_recv(socket, timeout)
        if result:
            result = self.mtool.unpack_msg(result)
        
        return result, details

if __name__ == '__main__':
    finder = NewEEGExperimentFinder(['tcp://127.0.0.1:54654'], zmq.Context())
    cnt, sock = finder.launch_discovery()

    # monitor_t = threading.Thread(target=finder.monitor_launching, args=[cnt])
    # monitor_t.daemon = True
    # monitor_t.start()

    if cnt.type != 'experiment_created':
        print "discovery experiment is not running"
        sys.exit(1)

    discov_params = finder.wait_for_discovery_registration(cnt)
    sss = json.dumps(discov_params, indent=4)
    print sss
    finder.client.kill_exp(cnt.uuid)

    # sock.close()
    # sock = finder.client.ctx.socket(zmq.REQ)
    # for addr in cnt.rep_addrs:
    #     sock.connect(addr)
    
    # time.sleep(10)
    
    # if sock:
    #     finder.request_available_drivers(sock)

    #     drivers = ''
    #     result = ''
    #     trials = 3
    #     while trials:#not drivers and not result and trials:
    #         print 'trials left:', trials, '\n\n\n\n'
    #         drivers, msg = finder.receive_available_drivers(sock)
    #         print drivers
    #         time.sleep(1)
    #         trials -= 1
    #     # print drivers
    #     finder.client.kill_exp(cnt.uuid)
    # else:
    #     print "FAIL"
        
