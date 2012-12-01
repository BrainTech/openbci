#!/usr/bin/python
# -*- coding: utf-8 -*-

import SocketServer
import zmq
import threading
import socket
import time

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from obci.control.common.obci_control_settings import PORT_RANGE
import obci.control.common.net_tools as net

DELIM = chr(ord(':')) #wtf
END = chr(ord(','))

class OBCIPeerTCP( SocketServer.TCPServer):#, SocketServer.ThreadingMixIn):
    allow_reuse_address = True
    def __init__(self, server_address, handler_class, bind_and_activate=True,
                            zmq_ctx=None, zmq_rep_addr=None):
        daemon_threads = True
        server_timeout = 45
        SocketServer.TCPServer.__init__(self,server_address, handler_class, bind_and_activate)
        self.mtool = OBCIMessageTool(message_templates)
        self.pl = PollingObject()
        self.ctx = zmq_ctx
        self.rep_addr = zmq_rep_addr


class OBCIServerTCP(OBCIPeerTCP):
    def __init__(self, server_address,  bind_and_activate=True,
                            zmq_ctx=None, zmq_rep_addr=None):
        # print server_address, requestHandlerClass
        OBCIPeerTCP.__init__(self,server_address, OBCIServerRequestHandler, bind_and_activate,
                        zmq_ctx, zmq_rep_addr)
        self.pull_sock = self.ctx.socket(zmq.PULL)
        self.pull_port = self.pull_sock.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)


class OBCIExperimentTCP(OBCIPeerTCP):
    def __init__(self, server_address, bind_and_activate=True,
                            zmq_ctx=None, zmq_rep_addr=None):
        OBCIPeerTCP.__init__(self, server_address, OBCIExperimentRequestHandler,
                bind_and_activate, zmq_ctx, zmq_rep_addr)

def run_tcp_obci_server(server_address, zmq_ctx, zmq_rep_addr):
    server = OBCIServerTCP(server_address, OBCIServerRequestHandler,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)
    return _run_tcp_server(server,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)

def run_tcp_obci_experiment(server_address, zmq_ctx, zmq_rep_addr):
    srv = OBCIExperimentTCP(server_address, OBCIExperimentRequestHandler,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)
    return _run_tcp_server(srv, zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)


def _run_tcp_server(server, zmq_ctx, zmq_rep_addr):
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server plain TCP loop running in thread:", server_thread.name
    print "serving on: ", server.server_address
    return server_thread, server, server.server_address

def _recv_netstring_len(rstream):
    bt = rstream.read(1)
    if bt == '':
        raise RuntimeError("socket connection broken")

    strlen = ''
    while bt != DELIM:
        print bt,
        if bt == '':
            raise RuntimeError("socket connection broken")
        strlen += bt
        bt = rstream.read(1)
    print ''
    return int(strlen)

def recv_netstring(rstream):
    datalen = _recv_netstring_len(rstream)
    data = rstream.read(datalen)
    got = len(data)
    do = 100
    while got < datalen and do:
        print "got", got, "len", datalen
        chunk = rstream.read(datalen - got)
        if chunk == '':
            raise RuntimeError("socket connection broken")
        data = ''.join([data, chunk])
        got += len(chunk)
        do -=1

    end = rstream.read(1)
    assert(end == END and got == datalen)
    return data

def recv_unicode_netstring(rstream):
    data = recv_netstring(rstream)
    msg = unicode(data, encoding='utf-8')
    return msg

def make_unicode_netstring(unicode_str):
    print 'unicode_len (characters): ', len(unicode_str)
    msg = unicode_str.encode('utf-8')
    return make_netstring(msg)

def make_netstring(bytes):
    datalen = len(bytes)
    print "encoded DATA LEN (bytes):", datalen
    return str(datalen) + DELIM + bytes + END


class OBCIPeerRequestHandler(SocketServer.StreamRequestHandler):

    def make_srv_sock(self):
        sock = self.server.ctx.socket(zmq.REQ)
        sock.connect(self.server.rep_addr)
        return sock

    def handle(self):
        message = recv_unicode_netstring(self.rfile)
        srv_sock = self.make_srv_sock()
        send_msg(srv_sock, message)
        pl = PollingObject()
        response, det = pl.poll_recv(srv_sock, timeout=5000)
        if not response:
            self.bad_response(self.wfile, det)
        self.rfile.write(make_unicode_netstring(response))

    def bad_response(self, rstream, details):
        print "baaaad", request, details
        err = self.server.mtool.fill_msg("rq_error", details=details)
        rstream.write(make_unicode_netstring(err))


class OBCIServerRequestHandler(OBCIPeerRequestHandler):
    def handle(self):
        print "SERVER REQUEST", self.__class__, "ME: ", self.request.getsockname()
        print "FROM :", self.request.getpeername()
        message = recv_unicode_netstring(self.rfile)
        print message
        pl = PollingObject()
        parsed = self.server.mtool.unpack_msg(message)
        if parsed.type == 'find_eeg_experiments' or parsed.type == 'find_eeg_amplifiers':
            pull_addr = 'tcp://' + socket.gethostname() + ':' + str(self.server.pull_port)
            parsed.client_push_address = pull_addr
        srv_sock = self.make_srv_sock()
        send_msg(srv_sock, parsed.SerializeToString())

        response, det = pl.poll_recv(srv_sock, timeout=5000)
        print "passed msg and got result:  ", response
        if not response:
            self.bad_response(self.wfile, det)
            return

        if parsed.type == 'find_eeg_experiments' or parsed.type == 'find_eeg_amplifiers':
            response, det = pl.poll_recv(self.server.pull_sock, timeout=20000)
            if not response:
                self.bad_response(self.wfile, det)
                return

        data = make_unicode_netstring(response)
        self.wfile.write(data)


class OBCIExperimentRequestHandler(OBCIPeerRequestHandler):
    pass


