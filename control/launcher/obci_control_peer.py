#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import uuid
import signal
import os
import sys
import threading
import time
import socket

import argparse

from obci.control.launcher.launcher_messages import message_templates
from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
import obci.control.common.net_tools as net
import obci.control.common.obci_control_settings as settings

from obci.control.launcher.subprocess_monitor import SubprocessMonitor
from obci.control.launcher.process import FAILED, TERMINATED, FINISHED, RUNNING, NON_RESPONSIVE
from obci.utils.openbci_logging import get_logger, log_crash
from obci.control.common import net_tools

class HandlerCollection(object):
    def __init__(self):
        self.handlers = {}
        self.default = self._default_handler
        self.error = self._error_handler
        self.unsupported = self._error_handler

    def new_from(other):
        return HandlerCollection._new_from(other)

    def copy(self):
        return HandlerCollection._new_from(self)

    def _new_from(other):
        new = HandlerCollection()
        new.handlers = dict(other.handlers)
        new.default = other.default
        new.error = other.error
        new.unsupported = other.unsupported
        return new

    def _default_handler(*args):
        pass

    def _error_handler(*args):
        pass

    def handler(self, message_type):
        def save_handler(fun):
            self.handlers[message_type] = fun
            return fun
        return save_handler

    def default_handler(self):
        def save_default_handler(fun):
            self.default = fun
            return fun
        return save_default_handler

    def error_handler(self):
        def save_error_handler(fun):
            self.error = fun
            return fun
        return save_error_handler

    def unsupported_handler(self):
        def save_unsupported_handler(fun):
            self.unsupported = fun
            return fun
        return save_unsupported_handler

    def handler_for(self, message_name):
        handler = self.handlers.get(message_name, None)

        return handler




class OBCIControlPeer(object):

    msg_handlers = HandlerCollection()

    def __init__(self, source_addresses=None,
                    rep_addresses=None, pub_addresses=None, name='obci_control_peer'):

        ###TODO TODO TODO !!!!
        ###cleaner subclassing of obci_control_peer!!!
        self.hostname = socket.gethostname()
        self.source_addresses = source_addresses if source_addresses else []
        self.rep_addresses = rep_addresses
        self.pub_addresses = pub_addresses
        self._all_sockets = []
        self._pull_addr = 'inproc://publisher_msg'
        self._push_addr = 'inproc://publisher'
        self._subpr_push_addr = 'inproc://subprocess_info'

        self.uuid = str(uuid.uuid4())
        self.name = str(name)
        self.type = self.peer_type()

        log_dir = os.path.join(settings.OBCI_CONTROL_LOG_DIR,
                                self.name + '-' + self.uuid[:8])
        if not hasattr(self, 'logger'):
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.logger = get_logger(self.peer_type(), log_dir=log_dir,
                    stream_level=net_tools.peer_loglevel())
            err_f = self.logger.error
            def _logger_error(*args, **kwargs):
                extra = kwargs.get('extra', {})
                tags = extra.get('tags', {})
                data = extra.get('data', {})
                tags.update(self._crash_extra_tags())
                data.update(self._crash_extra_data())
                extra['tags'] = tags
                extra['data'] = data
                kwargs['extra'] = extra
                return err_f(*args, **kwargs)
            self.logger.error = _logger_error

        self.mtool = self.message_tool()

        if not hasattr(self, "ctx"):
            self.ctx = zmq.Context()

        self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid, logger=self.logger)
        self.net_init()

        if self.source_addresses:
            self.registration_response = self.register()
            self._handle_registration_response(self.registration_response)
        else: self.registration_response = None

        self.interrupted = False
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())



    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("[!!!!] %s %s %s %s",
                        self.name, "got signal", signum, frame)
            self.interrupted = True
        return handler

    def peer_type(self):
        return 'obci_control_peer'

    def message_tool(self):
        return OBCIMessageTool(message_templates)

    def _publisher_thread(self, pub_addrs, pull_address, push_addr):
        #FIXME aaaaahhh pub_addresses are set here, not in the main thread
        # (which reads them in _register method)
        pub_sock, self.pub_addresses = self._init_socket(
                                    pub_addrs, zmq.PUB)

        pull_sock = self.ctx.socket(zmq.PULL)
        pull_sock.bind(pull_address)

        push_sock = self.ctx.socket(zmq.PUSH)
        push_sock.connect(push_addr)

        send_msg(push_sock, u'1')
        po = PollingObject()

        while not self._stop_publishing:
            try:
                to_publish, det = po.poll_recv(pull_sock, 500)

                if to_publish:
                    send_msg(pub_sock, to_publish)

            except:
                #print self.name, '.Publisher -- STOP.'
                break
        # self.logger.info( "close  sock %s %s", pub_addrs, pub_sock)
        pub_sock.close()
        pull_sock.close()
        push_sock.close()

    def _subprocess_info(self, push_addr):
        push_sock = self.ctx.socket(zmq.PUSH)
        push_sock.connect(push_addr)

        send_msg(push_sock, u'1')
        while not self._stop_monitoring:
            dead = self.subprocess_mgr.not_running_processes()
            if dead:
                # self.logger.warning("DEAD  process" +  str(dead))
                for key, status in dead.iteritems():
                    send_msg(push_sock, self.mtool.fill_msg('dead_process', machine=key[0],
                                                        pid=key[1], status=status))
            time.sleep(1)
        push_sock.close()


    def _push_sock(self, ctx, addr):
        sock = ctx.socket(zmq.PUSH)
        sock.connect(addr)
        return sock

    def _prepare_publisher(self):
        tmp_pull = self.ctx.socket(zmq.PULL)
        tmp_pull.bind(self._pull_addr)
        self.pub_thr = threading.Thread(target=self._publisher_thread,
                                        args=[self.pub_addresses,
                                            self._push_addr,
                                            self._pull_addr])
        self.pub_thr.daemon = True

        self._stop_publishing = False
        self.pub_thr.start()
        recv_msg(tmp_pull)
        self._publish_socket = self._push_sock(self.ctx, self._push_addr)
        self._all_sockets.append(self._publish_socket)
        tmp_pull.close()

    def _prepare_subprocess_info(self):
        self._subprocess_pull = self.ctx.socket(zmq.PULL)
        self._subprocess_pull.bind(self._subpr_push_addr)

        self.subprocess_thr = threading.Thread(target=self._subprocess_info,
                                            args=[self._subpr_push_addr])
        self.subprocess_thr.daemon = True
        self._stop_monitoring = False

        self.subprocess_thr.start()
        recv_msg(self._subprocess_pull)

        self._all_sockets.append(self._subprocess_pull)


    def net_init(self):
        # (self.pub_socket, self.pub_addresses) = self._init_socket(
        #                                         self.pub_addresses, zmq.PUB)
        self._all_sockets = []
        self._prepare_publisher()
        self._prepare_subprocess_info()

        (self.rep_socket, self.rep_addresses) = self._init_socket(
                                                self.rep_addresses, zmq.REP)
        self.rep_socket.setsockopt(zmq.LINGER, 0)
        self._all_sockets.append(self.rep_socket)

        print "\n\tname: {0}\n\tpeer_type: {1}\n\tuuid: {2}\n".format(
                                    self.name, self.peer_type(), self.uuid)
        print "rep: {0}".format(self.rep_addresses)
        print "pub: {0}\n".format(self.pub_addresses)

        self.source_req_socket = self.ctx.socket(zmq.REQ)

        if self.source_addresses:
            for addr in self.source_addresses:
                self.source_req_socket.connect(addr)
        self._all_sockets.append(self.source_req_socket)
        self._set_poll_sockets()


    def _init_socket(self, addrs, zmq_type):
        # print self.peer_type(), "addresses for socket init:", addrs
        addresses = addrs if addrs else ['tcp://*']

        random_port = True if not addrs else False

        sock = self.ctx.socket(zmq_type)
        port = None
        try:
            for i, addr in enumerate(addresses):
                if random_port and net.is_net_addr(addr):
                    port = str(sock.bind_to_random_port(addr,
                                                min_port=settings.PORT_RANGE[0],
                                                max_port=settings.PORT_RANGE[1]))
                    addresses[i] = addr + ':' + str(port)
                else:
                    sock.bind(addr)
        except Exception, e:
            self.logger.critical("CRITICAL error: %s", str(e))
            raise(e)

        advertised_addrs = []
        for addr in addresses:
            if addr.startswith('tcp://*'):
                port = addr.rsplit(':', 1)[1]
                advertised_addrs.append('tcp://' + socket.gethostname() + ':' +str(port))
                advertised_addrs.append('tcp://' + 'localhost:' + str(port))
            else:
                advertised_addrs.append(addr)
        return sock, advertised_addrs


    def _register(self, rep_addrs, pub_addrs, params):
        message = self.mtool.fill_msg("register_peer", peer_type=self.type,
                                                uuid=self.uuid,
                                                rep_addrs=rep_addrs,
                                                pub_addrs=pub_addrs,
                                                name=self.name,
                                                other_params=params)
        self.logger.debug("_register()  " + str(message))
        send_msg(self.source_req_socket, message)
        response_str = recv_msg(self.source_req_socket)
        response = self.mtool.unpack_msg(response_str)
        if response.type == "rq_error":
            self.logger.critical("Registration failed: {0}".format(response_str))
            sys.exit(2)
        return response

    def register(self):
        params = self.params_for_registration()
        return self._register(self.rep_addresses, self.pub_addresses, params)

    def _handle_registration_response(self, response):
        pass

    def shutdown(self):
        self.logger.info("SHUTTING DOWN")
        sys.exit(0)

    def params_for_registration(self):
        return {}

    def basic_sockets(self):
        return [self.rep_socket, self._subprocess_pull]

    def custom_sockets(self):
        """
        subclass this
        """
        return []

    def all_sockets(self):
        return self.basic_sockets() + self.custom_sockets()

    def _set_poll_sockets(self):
        self._poll_sockets = self.all_sockets()

    @log_crash
    def run(self):
        self.pre_run()
        poller = zmq.Poller()
        poll_sockets = list(self._poll_sockets)
        for sock in poll_sockets:
            poller.register(sock, zmq.POLLIN)

        try:
            while True:
                socks = []
                try:
                    socks = dict(poller.poll())
                except zmq.ZMQError, e:
                    self.logger.error(": zmq.poll(): " +str(    e.strerror))
                for sock in socks:
                    if socks[sock] == zmq.POLLIN:
                        more = True
                        while more:
                            try:
                                msg = recv_msg(sock, flags=zmq.NOBLOCK)
                            except zmq.ZMQError, e:
                                if e.errno == zmq.EAGAIN or sock.getsockopt(zmq.TYPE) == zmq.REP:
                                    more = False
                                else:
                                    self.logger.error("handling socket read error: %s  %d  %s",
                                                        e, e.errno, sock)
                                    poller.unregister(sock)
                                    if sock in poll_sockets:
                                        poll_sockets.remove(sock)
                                    self.handle_socket_read_error(sock, e)
                                    break
                            else:
                                self.handle_message(msg, sock)
                    else:
                        self.logger.warning("sock not zmq.POLLIN! Ignore !")

                if self.interrupted:
                    break
                self._update_poller(poller, poll_sockets)
        except Exception, e:
            # from urllib2 import HTTPError
            # try:
            #     self.logger.critical("UNHANDLED EXCEPTION IN %s!!! ABORTING!  Exception data: %s, e.args: %s, %s",
            #                         self.name, e, e.args, vars(e), exc_info=True,
            #                         extra={'stack': True})
            # except HTTPError, e:
            #     self.logger.info('sentry sending failed....')
            self._clean_up()
            raise(e)


    def _crash_extra_description(self, exception=None):
        return ""

    def _crash_extra_data(self, exception=None):
        return {}

    def _crash_extra_tags(self, exception=None):
        return {'obci_part' : 'launcher'}

    def _update_poller(self, poller, curr_sockets):
        self._set_poll_sockets()
        new_sockets = list(self._poll_sockets)

        for sock in new_sockets:
            if not sock in curr_sockets:
                poller.register(sock, zmq.POLLIN)
        for sock in curr_sockets:
            if not sock in new_sockets:
                poller.unregister(sock)
        curr_sockets = new_sockets

    def handle_socket_read_error(self, socket, error):
        pass


    def pre_run(self):
        pass

    def _clean_up(self):
        time.sleep(0.01)
        self._stop_publishing = True
        self._stop_monitoring = True
        self.pub_thr.join()
        self.subprocess_thr.join()

        for sock in self._all_sockets:
            #print self.name, "closing ", sock
            sock.close()
        # try:
        #     self.ctx.term()
        # except zmq.ZMQError(), e:
        #     print "Ctx closing interrupted."
        self.clean_up()

    def clean_up(self):
        self.logger.info("CLEANING UP")


########## message handling ######################################

    def handle_message(self, message, sock):

        handler = self.msg_handlers.default

        try:
            msg = self.mtool.unpack_msg(message)
            if msg.type != "ping" and msg.type != "rq_ok":
                self.logger.debug("got message: {0}".format(msg.type))
                if msg.type == "get_tail":
                    print self.msg_handlers
        except ValueError, e:
            print "{0} [{1}], Bad message format! {2}".format(
                                    self.name, self.peer_type(),message)
            if sock.getsockopt(zmq.TYPE) == zmq.REP:
                handler = self.msg_handlers.error
            msg = message
            print str(e)
        else:
            msg_type = msg.type


            handler = self.msg_handlers.handler_for(msg_type)
            if handler is None:
                # print "{0} [{1}], Unknown message type: {2}".format(
                #                         self.name, self.peer_type(),msg_type)
                # print message

                handler = self.msg_handlers.unsupported
        handler(self, msg, sock)

    @msg_handlers.handler("register_peer")
    def handle_register_peer(self, message, sock):
        """Subclass this."""
        result = self.mtool.fill_msg("rq_error",
            request=vars(message), err_code="unsupported_peer_type")
        send_msg(sock, result)

    @msg_handlers.handler("ping")
    def handle_ping(self, message, sock):
        if sock.socket_type in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, self.mtool.fill_msg("pong"))

    @msg_handlers.default_handler()
    def default_handler(self, message, sock):
        """Ignore message"""
        pass

    @msg_handlers.unsupported_handler()
    def unsupported_msg_handler(self, message, sock):
        if sock.socket_type in [zmq.REP, zmq.ROUTER]:
            msg = self.mtool.fill_msg("rq_error",
                    request=vars(message), err_code="unsupported_msg_type", sender=self.uuid)
            send_msg(sock, msg)
        # print "--"

    @msg_handlers.error_handler()
    def bad_msg_handler(self, message, sock):
        msg = self.mtool.fill_msg("rq_error",
                    request=message, err_code="invalid_msg_format")
        send_msg(sock, msg)

    @msg_handlers.handler("kill")
    def handle_kill(self, message, sock):

        if not message.receiver or message.receiver == self.uuid:
            self.cleanup_before_net_shutdown(message, sock)
            self._clean_up()
            self.shutdown()

    @msg_handlers.handler("dead_process")
    def handle_dead_process(self, message, sock):
        pass

    def cleanup_before_net_shutdown(self, kill_message, sock=None):
        for sock in self._all_sockets:
            sock.close()


class RegistrationDescription(object):
    def __init__(self, uuid, name, rep_addrs, pub_addrs, machine, pid, other=None):
        self.machine_ip = machine
        self.pid = pid
        self.uuid = uuid
        self.name = name
        self.rep_addrs = rep_addrs
        self.pub_addrs = pub_addrs
        self.other = other

    def info(self):
        return dict(machine=self.machine_ip, pid=self.pid, uuid=self.uuid, name=self.name,
                        rep_addrs=self.rep_addrs, pub_addrs=self.pub_addrs, other=self.other)


def basic_arg_parser():
    parser = argparse.ArgumentParser(add_help=False,
                    description='Basic OBCI control peer with public PUB and REP sockets.')
    parser.add_argument('--sv-addresses', nargs='+',
                        help='REP Addresses of the peer supervisor,\
    for example an OBCI Experiment controller may need OBCI Server addresses')
    parser.add_argument('--rep-addresses', nargs='+',
                        help='REP Addresses of the peer.')
    parser.add_argument('--pub-addresses', nargs='+',
                        help='PUB Addresses of the peer.')

    return parser


class OBCIControlPeerError(Exception):
    pass

class MessageHandlingError(OBCIControlPeerError):
    pass

if __name__ == '__main__':

    parser = argparse.ArgumentParser(parents=[basic_arg_parser()])
    parser.add_argument('--name', default='obci_control_peer',
                       help='Human readable name of this process')
    args = parser.parse_args()

    peer = OBCIControlPeer(args.sv_addresses,
                            args.rep_addresses, args.pub_addresses, args.name)

    peer.run()
