#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import sys
import time

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from common.obci_control_settings import PORT_RANGE
import common.net_tools as net


def update_nearby_servers(srv_data, lock, ctx=None):
    mtool = OBCIMessageTool(message_templates)

    ifname = net.server_ifname()
    my_addr = net.ext_ip(ifname=ifname)

    [subnet, my] = my_addr.rsplit('.', 1)
    router = 100

    ip_range = [subnet + '.' + str(i) for i in range(256)\
                                        if i not in [int(my), router]]
    srv_port = net.server_rep_port()

    poller = zmq.Poller()

    if ctx is None:
        ctx = zmq.Context()

    srv_dict = {}
    for ip in ip_range:
        req_s = ctx.socket(zmq.REQ)
        req_s.connect('tcp://' + ip + ':' + str(srv_port))
        srv_dict[req_s] =  ip
        poller.register(req_s, zmq.POLLIN)

    to_send = srv_dict.keys()

    while True:
        new_srv_data = []
        for sock in to_send:
            send_msg(sock, mtool.fill_msg('ping'))

        active_sockets = None
        fail_det = None
        try:
            active_sockets = dict(poller.poll(timeout=2000))
        except zmq.ZMQError, e:
            fail_det = "obci_client: zmq.poll(): " + e.strerror
            return
        else:
            to_send = []
            for sock in active_sockets:
                if active_sockets[sock] == zmq.POLLIN:
                    msg = mtool.unpack_msg(recv_msg(sock))
                    to_send.append(sock)
                    new_srv_data.append(srv_dict[sock])

            with lock:
                srv_data[0:] = list(new_srv_data)

        time.sleep(3)