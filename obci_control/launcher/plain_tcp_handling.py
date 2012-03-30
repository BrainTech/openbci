#!/usr/bin/python
# -*- coding: utf-8 -*-

import SocketServer
import zmq
import threading
import socket
import time

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

from common.obci_control_settings import PORT_RANGE
import common.net_tools as net

DELIM = chr(ord(':')) #wtf
END = chr(ord(','))

class OBCIPeerTCP( SocketServer.TCPServer, SocketServer.ThreadingMixIn):
    allow_reuse_address = True
    def __init__(self, server_address,  bind_and_activate=True,
                            zmq_ctx=None, zmq_rep_addr=None):
        SocketServer.TCPServer.__init__(self,server_address, OBCIServerRequestHandler, bind_and_activate)
        self.mtool = OBCIMessageTool(message_templates)
        self.pl = PollingObject()
        self.ctx = zmq_ctx
        self.rep_addr = zmq_rep_addr


class OBCIServerTCP(OBCIPeerTCP):
    def __init__(self, server_address,  bind_and_activate=True,
                            zmq_ctx=None, zmq_rep_addr=None):
        # print server_address, requestHandlerClass
        OBCIPeerTCP.__init__(self,server_address,  bind_and_activate,
                        zmq_ctx, zmq_rep_addr)
        self.pull_sock = self.ctx.socket(zmq.PULL)
        self.pull_port = self.pull_sock.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)


class OBCIExperimentTCP(OBCIPeerTCP):
    pass

def run_tcp_obci_server(server_address, zmq_ctx, zmq_rep_addr):
    return run_tcp_server(OBCIServerTCP, server_address, OBCIServerRequestHandler,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)

def run_tcp_obci_experiment(server_address, zmq_ctx, zmq_rep_addr):
    return run_tcp_server(OBCIExperimentTCP, server_address, OBCIExperimentRequestHandler,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)

def run_tcp_server(server_class, server_address, handler_class, zmq_ctx, zmq_rep_addr):
    server = server_class(server_address, handler_class,
                            zmq_ctx=zmq_ctx, zmq_rep_addr=zmq_rep_addr)
    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server plain TCP loop running in thread:", server_thread.name
    print "serving on: ", server.server_address
    return server_thread, server, server.server_address

def _recv_netstring_len(request):
    bt = request.recv(1)
    strlen = ''
    while bt != DELIM:
        print bt,
        strlen += bt
        bt = request.recv(1)
    print ''
    return int(strlen)

def recv_netstring(request):
    datalen = _recv_netstring_len(request)
    data = request.recv(datalen)
    got = len(data)
    do = 100
    while got < datalen and do:
        print "got", got, "len", datalen
        chunk = request.recv(datalen - got)
        if chunk == '':
            raise RuntimeError("socket connection broken")
        data = ''.join([data, chunk])
        got += len(chunk)
        do -=1

    end = request.recv(1)
    assert(end == END and got == datalen)
    return data

def recv_unicode_netstring(request):
    data = recv_netstring(request)
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


class OBCIPeerRequestHandler(SocketServer.BaseRequestHandler):
    def make_srv_sock(self):
        sock = self.server.ctx.socket(zmq.REQ)
        sock.connect(self.server.rep_addr)
        return sock

    def handle(self):
        message = recv_unicode_netstring(self.request)
        srv_sock = self.make_srv_sock()
        send_msg(srv_sock, message)

        response, det = self.server.pl.poll_recv(srv_sock, timeout=5000)
        if not response:
            self.bad_response(self,request, det)
        self.request.sendall(make_unicode_netstring(response))
        time.sleep(0.5)

    def bad_response(self, request, details):
        print "baaaad", request, details
        err = self.server.mtool.fill_msg("rq_error", details=details)
        request.sendall(make_unicode_netstring(err))

    def finish(self):
        print "TCP REQUEST HANDLER FINISHED!"

class OBCIServerRequestHandler(OBCIPeerRequestHandler):
    def handle(self):
        print "SERVER REQUEST", self.__class__
        print "FROM :", self.request.getpeername()
        message = recv_unicode_netstring(self.request)
        print message
        parsed = self.server.mtool.unpack_msg(message)
        if parsed.type == 'find_eeg_experiments' or parsed.type == 'find_eeg_amplifiers':
            pull_addr = 'tcp://' + socket.gethostname() + ':' + str(self.server.pull_port)
            parsed.client_push_address = pull_addr
        srv_sock = self.make_srv_sock()
        send_msg(srv_sock, parsed.SerializeToString())

        response, det = self.server.pl.poll_recv(srv_sock, timeout=5000)
        print "passed msg and got result:  ", response
        if not response:
            self.bad_response(self.request, det)
            return

        if parsed.type == 'find_eeg_experiments' or parsed.type == 'find_eeg_amplifiers':
            response, det = self.server.pl.poll_recv(self.server.pull_sock, timeout=20000)
            if not response:
                self.bad_response(self.request, det)
                return

        data = make_unicode_netstring(response)
        to_send = len(data)
        print "TO SEND: ", to_send
        sent = 0
        while sent < to_send:
            out = self.request.send(data[sent:])
            if out == 0:
                raise RuntimeError("socket connection broken")
            print "chunk sent: ", out
            sent += out
        # result = self.request.sendall(make_unicode_netstring(response))
        print "REsult", result
        # time.sleep(3)


class OBCIExperimentRequestHandler(OBCIPeerRequestHandler):
    def handle(self):
        print "(exp) FROM : ", self.request.getpeername()
        print "(exp) ME: ", self.request.getsockname()
        super(OBCIExperimentRequestHandler, self).handle()

