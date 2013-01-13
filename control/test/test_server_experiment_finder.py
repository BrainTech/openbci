#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import sys
import socket

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from obci.control.launcher.launcher_messages import message_templates, error_codes

from obci.control.common.obci_control_settings import PORT_RANGE
import obci.control.common.net_tools as net

if __name__ == '__main__':
    mtool = OBCIMessageTool(message_templates)
    pl = PollingObject()

    # ifname = net.server_ifname()
    my_addr = 'tcp://' + 'localhost'

    ctx = zmq.Context()

    server_req = ctx.socket(zmq.REQ)
    server_req.connect(my_addr + ':' + net.server_rep_port())

    exp_info_pull = ctx.socket(zmq.PULL)

    port = exp_info_pull.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)

    client_push_addr = my_addr + ':' + str(port)
    print client_push_addr

    send_msg(server_req, mtool.fill_msg('find_eeg_experiments',
                                    client_push_address=client_push_addr))
    msg,details = pl.poll_recv(server_req, 5000)
    if not msg:
        print "srv request timeout!"
        server_req.close()
        sys.exit(1)

    response = mtool.unpack_msg(msg)

    if not response.type == 'rq_ok':
        print "whaaa?"
        sys.exit(1)

    msg, details = pl.poll_recv(exp_info_pull, 20000)

    if not msg:
        print "TIMEOUT"
    else:
        exp_info = mtool.unpack_msg(msg)
        sss = json.dumps(exp_info.experiment_list, indent=4)
        #print sss
        print len(sss)
        print [(exp['rep_addr'], exp['experiment_info']['name']) for exp in exp_info.experiment_list]

    send_msg(server_req, mtool.fill_msg('find_eeg_amplifiers',
                                    client_push_address=client_push_addr))
    msg,details = pl.poll_recv(server_req, 5000)
    if not msg:
        print "srv request timeout!"
        server_req.close()
        sys.exit(1)
    response = mtool.unpack_msg(msg)

    if not response.type == 'rq_ok':
        print response
        print "whaaa?"
        sys.exit(1)

    msg, details = pl.poll_recv(exp_info_pull, 20000)
    print msg
