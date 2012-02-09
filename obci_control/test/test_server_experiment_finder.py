#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import sys

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from common.obci_control_settings import PORT_RANGE
import common.net_tools as net

if __name__ == '__main__':
    mtool = OBCIMessageTool(message_templates)

    ifname = net.server_ifname()
    my_addr = 'tcp://' + net.ext_ip(ifname=ifname)

    ctx = zmq.Context()

    server_req = ctx.socket(zmq.REQ)
    server_req.connect(net.server_address(ifname=ifname))

    exp_info_pull = ctx.socket(zmq.PULL)

    port = exp_info_pull.bind_to_random_port(my_addr,
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)

    client_push_addr = my_addr + ':' + str(port)
    print client_push_addr

    send_msg(server_req, mtool.fill_msg('find_eeg_experiments',
                                    client_push_address=client_push_addr))
    msg = recv_msg(server_req)
    response = mtool.unpack_msg(msg)

    if not response.type == 'rq_ok':
        print "whaaa?"
        sys.exit(1)

    msg = recv_msg(exp_info_pull)
    exp_info = mtool.unpack_msg(msg)

    print exp_info.experiment_list
