#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import socket
from common.message import OBCIMessageTool
import common.net_tools as net

from launcher.launcher_messages import message_templates

from launcher.plain_tcp_handling import make_unicode_netstring, recv_unicode_netstring


mtool = OBCIMessageTool(message_templates)

def get_eeg_experiments(host, port):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    msg = mtool.fill_msg("find_eeg_experiments")
    netstr = make_unicode_netstring(msg)

    try:
        # Connect to server and send data
        sock.connect((host, port))
        sock.sendall(netstr)

        # Receive data from the server and shut down
        received = recv_unicode_netstring(sock)
        print received
        print received.__class__, received[0], received[-1]
        msg = mtool.unpack_msg(received)
        if msg.type == 'rq_error':
            print 'BLEEEEEEEEE'
        else:
            print msg.experiment_list
    finally:
        sock.close()

if __name__ == '__main__':
    get_eeg_experiments(socket.gethostname(), int(net.server_tcp_proxy_port()))