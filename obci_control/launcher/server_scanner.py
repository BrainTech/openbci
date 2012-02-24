#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import sys
import time
from socket import *
import Queue
import select
import threading

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from common.obci_control_settings import PORT_RANGE
import common.net_tools as net


UPDATE_INTERVAL = 8
_LOOPS = 3

ALLOWED_SILENCE = 45

def update_nearby_servers(srv_data, srv_data_lock, bcast_port, ctx=None):
    mtool = OBCIMessageTool(message_templates)

    loops_to_update = _LOOPS
    servers = {}

    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', bcast_port))

    update_timeout = False
    def timer_end():
        update_timeout = True

    while 1:
        try:
            inp, out, exc = select.select([s], [], [], UPDATE_INTERVAL / _LOOPS)
        except Exception, e:
            print "nearby_servers_update - exception:", str(e)
            print "nearby_servers_update - aborting."
            return

        if s in inp:
            data, wherefrom = s.recvfrom(1500, 0)
            # sys.stderr.write(repr(wherefrom) + '\n')
            # sys.stdout.write(data)
            msg = unicode(data, encoding='utf-8')
            msg = msg[:-1]
            message = mtool.unpack_msg(msg)
            servers[wherefrom[0]] = (time.time(), message)

        else:
            # print "no data"
            pass
        
        loops_to_update -= 1

        if loops_to_update == 0:
            loops_to_update = _LOOPS
        
            keys = servers.keys()
            for ip in keys:
                timestamp, srv = servers[ip]
                check_time = time.time()
                if timestamp + ALLOWED_SILENCE < check_time:
                    print "[obci_server] obci_server on", ip, ',', servers[ip][1].sender_ip, "is most probably down."
                    del servers[ip]
        
            with srv_data_lock:
                srv_data.update(servers)
                keys = srv_data.keys()
                for ip in keys:
                    if ip not in servers:
                        del srv_data[ip]

    s.close()

def broadcast_server(server_uuid, rep_port, pub_port, bcast_port):
    mtool = OBCIMessageTool(message_templates)

    msg = mtool.fill_msg("server_broadcast", sender_ip=gethostname(), sender=server_uuid,
                                rep_port=rep_port, pub_port=pub_port)
    msg += u'\n'
    str_msg = msg.encode('utf-8')

    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    while 1:
        try:
            s.sendto(str_msg, ('<broadcast>', bcast_port))
        except error, e:
            print "[obci_server] Cannot broadcast obci_server, will try again in 1min:", str(e)
            time.sleep(53)
        time.sleep(7)

    s.close()