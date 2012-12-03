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

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from obci.control.launcher.launcher_messages import message_templates, error_codes

from obci.control.common.obci_control_settings import PORT_RANGE
import obci.control.common.net_tools as net


UPDATE_INTERVAL = 8
_LOOPS = 3

ALLOWED_SILENCE = 45

def update_nearby_servers(srv_data, bcast_port, ctx=None, update_push_addr=None):
    mtool = OBCIMessageTool(message_templates)

    loops_to_update = _LOOPS

    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(('', bcast_port))

    notify_sock = None
    if update_push_addr is not None:
        ctx = ctx if ctx else zmq.Context()
        notify_sock = ctx.socket(zmq.PUSH)
        notify_sock.connect(update_push_addr)

    while 1:
        changed = False
        try:
            inp, out, exc = select.select([s], [], [], UPDATE_INTERVAL / _LOOPS)
        except Exception, e:
            srv_data.logger.critical("nearby_servers_update - exception: %s", str(e))
            srv_data.logger.critical("nearby_servers - aborting")
            return

        if s in inp:
            data, wherefrom = s.recvfrom(1500, 0)
            # sys.stderr.write(repr(wherefrom) + '\n')
            # sys.stdout.write(data)
            msg = unicode(data, encoding='utf-8')
            msg = msg[:-1]
            message = mtool.unpack_msg(msg)
            changed = srv_data.update(ip=wherefrom[0], hostname=message.sender_ip,
                                uuid=message.sender, rep_port=message.rep_port,
                                pub_port=message.pub_port)

        else:
            # print "no data"
            pass

        loops_to_update -= 1

        if loops_to_update == 0:
            loops_to_update = _LOOPS
            changed = srv_data.clean_silent()

        if changed:
            send_msg(notify_sock, mtool.fill_msg('nearby_machines',
                                                nearby_machines=srv_data.dict_snapshot()))

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

    # introduction
    for i in range(10):
        try:
            s.sendto(str_msg, ('<broadcast>', bcast_port))
        except error, e:
            pass
        time.sleep(0.3)

    # updates
    while 1:
        try:
            s.sendto(str_msg, ('<broadcast>', bcast_port))
        except error, e:
            print "[obci_server] Cannot broadcast obci_server, will try again in 1min:", str(e)
            time.sleep(53)
        time.sleep(7)

    s.close()
