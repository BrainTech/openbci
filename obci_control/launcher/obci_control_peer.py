#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import uuid
import signal
import sys

import argparse

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates
import common.net_tools as net
import common.obci_control_settings as settings

class OBCIControlPeer(object):

	def __init__(self, obci_install_dir, source_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_control_peer'):

		###TODO TODO TODO !!!!
		###cleaner subclassing of obci_control_peer!!!
		self.source_addresses = source_addresses if source_addresses else []
		self.rep_addresses = rep_addresses
		self.pub_addresses = pub_addresses
		self.obci_dir = obci_install_dir

		self.uuid = str(uuid.uuid4())
		self.name = str(name)
		self.type = self.peer_type()

		self.mtool = self.message_tool()

		self.ctx = zmq.Context()

		self.net_init()

		if self.source_addresses:
			self.register()

		self.interrupted = False
		signal.signal(signal.SIGTERM, self.signal_handler())
		signal.signal(signal.SIGINT, self.signal_handler())


	def signal_handler(self):
		def handler(signum, frame):
			#print "Process {0} (uuid {1}) interrupted!\
#Signal: {2}, frame: {3}".format(self.name, self.uuid, signum, frame)
			self.interrupted = True
		return handler

	def peer_type(self):
		return 'obci_control_peer'

	def message_tool(self):
		return OBCIMessageTool(message_templates)

	def net_init(self):
		(self.pub_socket, self.pub_addresses) = self._init_socket(
												self.pub_addresses, zmq.PUB)
		(self.rep_socket, self.rep_addresses) = self._init_socket(
												self.rep_addresses, zmq.REP)

		print "\nname: {0}, uuid: {1}".format(self.name, self.uuid)
		print "rep: {0}".format(self.rep_addresses)
		print "pub: {0}\n".format(self.pub_addresses)

		self.source_req_socket = self.ctx.socket(zmq.REQ)
		if self.source_addresses:
			for addr in self.source_addresses:
				self.source_req_socket.connect(addr)
		self._set_poll_sockets()

	def _init_socket(self, addrs, zmq_type, create_ipc=True):

		ipc_name=''
		if not addrs:
			addresses = [addr for addr in self.source_addresses \
												if net.is_net_addr(addr)]
			if not self.source_addresses:
				addresses = ["tcp://"+net.lo_ip(), "tcp://"+net.ext_ip()]
			random_port = True
			if create_ipc:
				ipc_name=self.name+'.'+self.uuid
		else:
			addresses = addrs
			random_port = False
			if not [addr for addr in addresses if not net.is_net_addr(addr)] and create_ipc:
				ipc_name=self.name+'.'+self.uuid
			if not [addr for addr in addresses if net.is_net_addr(addr)]:
				addresses += ["tcp://"+net.lo_ip(), "tcp://"+net.ext_ip()]
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
		send_msg(self.source_req_socket, message)
		response_str = recv_msg(self.source_req_socket)
		response = self.mtool.unpack_msg(response_str)
		if response.type == "rq_error":
			print "Registration failed: {0}".format(response_str)
			sys.exit(2)

	def register(self):
		params = self.params_for_registration()
		self._register(self.rep_addresses, self.pub_addresses, params)

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
				print self.name +": zmq.poll(): " + e.strerror

			for sock in socks:
				if socks[sock] == zmq.POLLIN:
					msg = recv_msg(sock)
					self.handle_message(msg, sock)

			if self.interrupted:
				break

			self._update_poller(poller, poll_sockets)

		self.clean_up()


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

	def clean_up(self):
		print "Cleaning up"


########## message handling ######################################

	def handle_message(self, message, sock):
		handler = self.default_handler
		try:
			msg = self.mtool.unpack_msg(message)
			print "{0} [{1}], got message: {2}".format(self.name, self.peer_type(), msg.type)
		except ValueError:
			print "Bad message format! {0}".format(message)
			if sock.getsockopt(zmq.TYPE) == zmq.REP:
				handler = self.bad_msg_handler
		else:
			msg_type = msg.type

			try:
				handler = getattr(self, "handle_" + msg_type)
			except AttributeError:
				print "Unknown message type: {0}".format(msg_type)
				print message
				if sock.getsockopt(zmq.TYPE) == zmq.REP:
					handler = self.unsupported_msg_handler

		handler(msg, sock)

	def handle_register_peer(self, message, sock):
		result = self.mtool.fill_msg("rq_error",
			request=vars(message), err_code="unsupported_peer_type")
		send_msg(sock, result)

	def handle_ping(self, message, sock):
		if sock.socket_type in [zmq.REP, zmq.ROUTER]:
			send_msg(sock, self.mtool.fill_msg("pong"))

	def default_handler(self, message, sock):
		"""Ignore message"""
		pass

	def unsupported_msg_handler(self, message, sock):
		if sock.socket_type in [zmq.REP, zmq.ROUTER]:
			msg = self.mtool.fill_msg("rq_error",
					request=vars(message), err_code="unsupported_msg_type")
			send_msg(sock, msg)

	def bad_msg_handler(self, message, sock):
		msg = self.mtool.fill_msg("rq_error",
					request=vars(message), err_code="invalid_msg_format")
		send_msg(sock, msg)

	def handle_kill(self, message, sock):

		if not message.receiver or message.receiver == self.uuid:
			self.cleanup_before_net_shutdown(message, sock)
			self.shutdown()

	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		pass

class RegistrationDescription(object):
	def __init__(self, uuid, name, rep_addrs, pub_addrs, machine, pid, other=None):
		self.machine = machine
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
							args.rep_addresses, args.pub_addresses, args.name)
	peer.run()