#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import uuid
import signal

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
		self.source_addresses = source_addresses
		self.rep_addresses = rep_addresses
		self.pub_addresses = pub_addresses
		self.obci_dir = obci_install_dir

		self.uuid = str(uuid.uuid4())
		self.name = str(name)
		self.type = self.peer_type()

		self.mtool = self.message_tool()

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
		self.ctx = zmq.Context()

		(self.pub_socket, self.pub_addresses) = self._init_socket(
												self.pub_addresses, zmq.PUB)

		(self.rep_socket, self.rep_addresses) = self._init_socket(
												self.rep_addresses, zmq.REP)

		print "\nname: {0}, uuid: {1}".format(self.name, self.uuid)
		print "rep: {0}".format(self.rep_addresses)
		print "pub: {0}".format(self.pub_addresses)

		self.source_req_socket = None
		if self.source_addresses:
			self.source_req_socket = self.ctx.socket(zmq.REQ)
			for addr in addresses:
				self.source_req_socket.connect(addr)
		self._set_poll_sockets()

	def _init_socket(self, addrs, zmq_type):
		ipc_name=''
		if not addrs:
			addresses = self.source_addresses
			if not self.source_addresses:
				addresses = ["tcp://"+net.lo_ip(), "tcp://"+net.ext_ip()]
			random_port = True
			ipc_name=self.name+'.'+self.uuid
		else:
			addresses = addrs
			random_port = False
			if not [addr for addr in addresses if not net.is_net_addr(addr)]:
				ipc_name=self.name+'.'+self.uuid
			if not [addr for addr in addresses if net.is_net_addr(addr)]:
				addresses += ["tcp://"+net.lo_ip(), "tcp://"+net.ext_ip()]
				random_port = True

		return net.public_socket(addresses, zmq_type, self.ctx,
								ipc_core_name=ipc_name,
								random_port=random_port)


	def _register(self, rep_addrs, pub_addrs, params):
		message = self.mtool.fill_msg("register_peer", type=self.type,
												uuid=self.uuid,
												rep_addrs=rep_addrs,
												pub_addrs=pub_addrs,
												name=self.name,
												other_params=params)
		send_msg(self.source_req_socket, message)
		response_str = recv_msg(self.source_req_socket)
		response = self.mtool.decode_msg(response_str)
		if response["type"] == "rq_error":
			print "Registration failed: {0}".format(response_str)
			sys.exit(2)

	def register(self):
		params = self.params_for_registration()
		self._register(self.rep_addresses, self.pub_addresses, params)

	def shutdown(self):
		#TODO CLEAN!!!
		sys.exit(0)

	def params_for_registration(self):
		return {}

	def basic_sockets(self):
		return [self.pub_socket, self.rep_socket]

	def custom_sockets(self):
		"""
		subclass this
		"""
		return []

	def all_sockets(self):
		return self.basic_sockets() + self.custom_sockets()

	def _set_poll_sockets(self):
		self._poll_sockets = self.basic_sockets() + self.custom_sockets()

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
				print "zmq.poll(): " + e.strerror

			for sock in socks:
				if socks[sock] == zmq.POLLIN:
					msg = recv_msg(sock)
					self.handle_message(msg, sock)

			if self.interrupted:
				break

			self._update_poller(poller, poll_sockets)

		self.clean_up()


	def _update_poller(self, poller, curr_sockets):
		new_socks = list(self._poll_sockets)

		for sock in new_socks:
			if not sock in curr_sockets:
				poller.register(sock, zmq.POLLIN)
		for sock in curr_sockets:
			if not sock in new_sockets:
				poller.deregister(sock)
		curr_sockets = new_socks

	def pre_run(self):
		pass

	def clean_up(self):
		print "Cleaning up"


########## pass message handling ######################################

	def handle_message(self, message, sock):
		handler = self.default_handler
		try:
			msg = self.mtool.decode_msg(message)
		except ValueError:
			print "Bad message format! {0}".format(message)
			if sock.getsockopt(zmq.TYPE) == zmq.REP:
				handler = self.bad_msg_handler
		else:
			msg_type = msg["type"]

			try:
				handler = getattr(self, "handle_" + msg_type)
			except AttributeError:
				print "Unknown message type: {0}".format(msg_type)
				if sock.getsockopt(zmq.TYPE) == zmq.REP:
					handler = self.unsupported_msg_handler

		handler(msg, sock)

	def handle_register_peer(self, message, sock):
		result = self.mtool.fill_msg("rq_error",
			request=message, err_code="unsupported_peer_type")
		send_msg(sock, result)

	def default_handler(self, message, sock):
		"""Ignore message"""
		pass

	def unsupported_msg_handler(self, message, sock):
		msg = self.mtool.fill_msg("rq_error",
					request=message, err_code="unsupported_msg_type")
		send_msg(sock, msg)

	def bad_msg_handler(self, message, sock):
		msg = self.mtool.fill_msg("rq_error",
					request=message, err_code="invalid_msg_format")
		send_msg(sock, msg)

	def kill_handler(self, message, sock):
		msg = self.mtool.fill_msg("rq_ok", sender=self.uuid,
					status="trying_to_die")
		send_msg(sock, msg)
		self.shutdown()


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