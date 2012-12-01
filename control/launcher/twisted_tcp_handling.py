#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.protocols.basic import NetstringReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import zmq
import socket
import threading

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from obci.control.common.obci_control_settings import PORT_RANGE
import common.net_tools as net

class OBCIProxy(NetstringReceiver):

    def stringReceived(self, string):
        req_sock = self.factory.ctx.socket(zmq.REQ)
        req_sock.connect(self.factory.zmq_rep_addr)
        req = unicode(string, encoding='utf-8')
        print "twisted got:", req
        bad = False
        try:
            parsed = self.factory.mtool.unpack_msg(req)
        except ValueError:
            bad = True
	if not bad:
            if parsed.type in self.factory.long_rqs:
                sock, port = self.factory.long_rqs[parsed.type]
                pull_addr = 'tcp://' + socket.gethostname() + ':' + str(port)
                parsed.client_push_address = pull_addr
                send_msg(req_sock, parsed.SerializeToString())
            else:
                send_msg(req_sock, req)

        pl = PollingObject()
        msg, det = pl.poll_recv(req_sock, timeout=5000)
        if not msg:
            msg = self.factory.mtool.fill_msg("rq_error", details=det)

        if not bad:
            if parsed.type in self.factory.long_rqs:
                sock, port = self.factory.long_rqs[parsed.type]
                msg, det = pl.poll_recv(sock, timeout=20000)
                if not msg:
                    msg = self.factory.mtool.fill_msg("rq_error", details=det)
                    return

        encmsg = msg.encode('utf-8')
        self.sendString(encmsg)
        reactor.callFromThread(self.sendString, encmsg)



class OBCIProxyFactory(Factory):
    protocol = OBCIProxy

    def __init__(self, address, zmq_ctx, zmq_rep_addr):
        self.srv_address = address
        self.ctx = zmq_ctx
        self.zmq_rep_addr = zmq_rep_addr
        self.long_rqs = {}

        for msgtype in ["find_eeg_experiments",
                        "find_eeg_amplifiers",
                        #"join_experiment",
                        "start_eeg_signal"]:
            self.long_rqs[msgtype] = self._make_pull_sock()

        self.mtool = OBCIMessageTool(message_templates)

    def _make_pull_sock(self):
        sock = self.ctx.socket(zmq.PULL)
        port = sock.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)
        return (sock, port)


def run_twisted_server(address, zmq_ctx, zmq_rep_addr):
    fact = OBCIProxyFactory(address, zmq_ctx, zmq_rep_addr)
    port = reactor.listenTCP(address[1], fact)
    port = port.getHost().port
    fact.srv_address = (address[0], port)
    thr = threading.Thread(target=reactor.run, args=[False])
    thr.daemon = True
    thr.start()
    print "Twisted: listening on port", port
    return thr, port

if __name__ == '__main__':
    run_twisted_server(('0.0.0.0', 12013), zmq.Context(), 'tcp://127.0.0.1:54654')
    print "twisted: server started."
