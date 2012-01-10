#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import uuid
import signal
import sys
import threading

import argparse

from launcher_messages import message_templates
from common.message import OBCIMessageTool, send_msg, recv_msg
import common.net_tools as net
import common.obci_control_settings as settings


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

	def __init__(self, obci_install_dir, source_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_control_peer',
										ifname=None):

		###TODO TODO TODO !!!!
		###cleaner subclassing of obci_control_peer!!!
		self.source_addresses = source_addresses if source_addresses else []
		self.rep_addresses = rep_addresses
		self.pub_addresses = pub_addresses
		self._all_sockets = []
		self.obci_dir = obci_install_dir
		self._pull_addr = 'inproc://publisher_msg'
		self._push_addr = 'inproc://publisher'

		self.uuid = str(uuid.uuid4())
		self.name = str(name)
		self.type = self.peer_type()

		self.mtool = self.message_tool()

		if not hasattr(self, "ctx"):
			self.ctx = zmq.Context()

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

		while not self._stop_publishing:
			try:
				to_publish = recv_msg(pull_sock)

				send_msg(pub_sock, to_publish)
			except:
				#print self.name, '.Publisher -- STOP.'

				print "close  sock ", pub_addrs, pub_sock
				pub_sock.close()
				pull_sock.close()
				push_sock.close()
				break

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

	def net_init(self):
		# (self.pub_socket, self.pub_addresses) = self._init_socket(
		# 										self.pub_addresses, zmq.PUB)
		self._all_sockets = []
		self._prepare_publisher()

		(self.rep_socket, self.rep_addresses) = self._init_socket(
												self.rep_addresses, zmq.REP)
		self._all_sockets.append(self.rep_socket)

		print "\n\tname: {0}\n\tpeer_type: {1}\n\tuuid: {2}\n".format(
									self.name, self.peer_type(), self.uuid)
		#print "rep: {0}".format(self.rep_addresses)
		#print "pub: {0}\n".format(self.pub_addresses)

		self.source_req_socket = self.ctx.socket(zmq.REQ)

		if self.source_addresses:
			for addr in self.source_addresses:
				self.source_req_socket.connect(addr)
		self._all_sockets.append(self.source_req_socket)
		self._set_poll_sockets()

	def _init_socket(self, addrs, zmq_type, create_ipc=True):
		basic_addrs = [ "tcp://"+net.lo_ip(),
						"tcp://"+net.ext_ip(ifname=net.server_ifname())]
		ipc_name=''
		if not addrs:
			#addresses = [addr for addr in self.source_addresses \
			#									if net.is_net_addr(addr)]
			#if not self.source_addresses:
			addresses = basic_addrs
			random_port = True
			if create_ipc:
				ipc_name=self.name+'.'+self.uuid
		else:
			addresses = addrs
			random_port = False
			if not [addr for addr in addresses if not net.is_net_addr(addr)] and create_ipc:
				ipc_name=self.name+'.'+self.uuid
			if not [addr for addr in addresses if net.is_net_addr(addr)]:
				addresses += basic_addrs
				random_port = True

		return net.public_socket(addresses, zmq_type, self.ctx,
								ipc_core_name=ipc_name,
								random_port=random_port)


	def _register(self, rep_addrs, pub_addrs, params):
		message = self.mtool.fill_msg("register_peer", peer_type=self.type,
												uuid=self.uuid,
												rep_addrs=rep_addrs,
												pub_addrs=pub_addrs,
												name=self.name,
												other_params=params)
		print message
		send_msg(self.source_req_socket, message)
		response_str = recv_msg(self.source_req_socket)
		response = self.mtool.unpack_msg(response_str)
		if response.type == "rq_error":
			print "{0} [{1}] Registration failed: {2}".format(
										self.name, self.peer_type(),response_str)
			sys.exit(2)
		return response

	def register(self):
		params = self.params_for_registration()
		return self._register(self.rep_addresses, self.pub_addresses, params)

	def _handle_registration_response(self, response):
		pass

	def shutdown(self):
		print '{0} [{1}] -- IS SHUTTING DOWN'.format(self.name, self.peer_type())
		sys.exit(0)

	def params_for_registration(self):
		return {}

	def basic_sockets(self):
		return [self.rep_socket]

	def custom_sockets(self):
		"""
		subclass this
		"""
		return []

	def all_sockets(self):
		return self.basic_sockets() + self.custom_sockets()

	def _set_poll_sockets(self):
		self._poll_sockets = self.all_sockets()

	def run(self):
		self.pre_run()
		poller = zmq.Poller()
		poll_sockets = list(self._poll_sockets)
		for sock in poll_sockets:
			poller.register(sock, zmq.POLLIN)

		while True:
			socks = []
			try:
				socks = dict(poller.poll())
			except zmq.ZMQError, e:
				print self.name + ' ['+self.peer_type() + ']' +": zmq.poll(): " + e.strerror

			for sock in socks:
				if socks[sock] == zmq.POLLIN:
					msg = recv_msg(sock)
					self.handle_message(msg, sock)

			if self.interrupted:
				break

			self._update_poller(poller, poll_sockets)

		self._clean_up()


	def _update_poller(self, poller, curr_sockets):
		new_sockets = list(self._poll_sockets)

		for sock in new_sockets:
			if not sock in curr_sockets:
				poller.register(sock, zmq.POLLIN)
		for sock in curr_sockets:
			if not sock in new_sockets:
				poller.deregister(sock)
		curr_sockets = new_sockets


	def pre_run(self):
		pass

	def _clean_up(self):
		for sock in self._all_sockets:
			#print self.name, "closing ", sock
			sock.close()
		# try:
		# 	self.ctx.term()
		# except zmq.ZMQError(), e:
		# 	print "Ctx closing interrupted."
		self.clean_up()

	def clean_up(self):
		print "{0} [{1}], Cleaning up".format(self.name, self.peer_type())


########## message handling ######################################

	def handle_message(self, message, sock):

		handler = self.msg_handlers.default
		try:
			msg = self.mtool.unpack_msg(message)
			if msg.type != "ping":
				print "{0} [{1}], got message: {2}".format(
										self.name, self.peer_type(), msg.type)
				if msg.type == "get_tail":
					print self.msg_handlers
		except ValueError:
			print "{0} [{1}], Bad message format! {2}".format(
									self.name, self.peer_type(),message)
			if sock.getsockopt(zmq.TYPE) == zmq.REP:
				handler = self.msg_handlers.error
		else:
			msg_type = msg.type


			handler = self.msg_handlers.handler_for(msg_type)
			if handler is None:
				print "{0} [{1}], Unknown message type: {2}".format(
										self.name, self.peer_type(),msg_type)
				print message

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
		print "--"

	@msg_handlers.error_handler()
	def bad_msg_handler(self, message, sock):
		msg = self.mtool.fill_msg("rq_error",
					request=vars(message), err_code="invalid_msg_format")
		send_msg(sock, msg)

	@msg_handlers.handler("kill")
	def handle_kill(self, message, sock):

		if not message.receiver or message.receiver == self.uuid:
			self.cleanup_before_net_shutdown(message, sock)
			self._clean_up()
			self.shutdown()

	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		pass


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
		return dict(machine=self.machine, pid=self.pid, uuid=self.uuid, name=self.name,
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
	parser.add_argument('--obci-dir', default=settings.INSTALL_DIR,
						help='Main OpenBCI installation directory')
	parser.add_argument('--ifname', help='Name of the network interface in which this\
peer will be listening for requests.')

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
	print vars(args)
	peer = OBCIControlPeer(args.obci_dir, args.sv_addresses,
							args.rep_addresses, args.pub_addresses, args.name, args.ifname)
	print peer.msg_handlers.handlers["register_peer"]
	peer.run()