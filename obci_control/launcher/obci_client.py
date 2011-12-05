#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates, error_codes
from obci_control_peer import OBCIControlPeer, basic_arg_parser

import common.obci_control_settings as settings

class OBCIClient(object):

	default_timeout=5000

	def __init__(self, server_addresses, zmq_context=None):
		self.ctx = zmq_context if zmq_context else zmq.Context()

		self.server_req_socket = self.ctx.socket(zmq.REQ)
		for addr in server_addresses:
			self.server_req_socket.connect(addr)

		self.poller = zmq.Poller()
		self.poller.register(self.server_req_socket, zmq.POLLIN)

		self.mtool = OBCIMessageTool(message_templates)


	def launch(self, launch_file=None, sandbox_dir=None):
		result = self.send_create_experiment(launch_file, sandbox_dir)
		if not result:
			return result
		if result.type != "experiment_created":
			return result

		return self.send_start_experiment(result.rep_addrs)

	def send_start_experiment(self, exp_addrs):
		exp_sock = self.ctx.socket(zmq.REQ)
		for addr in exp_addrs:
			exp_sock.connect(addr)
		self.poller.register(exp_sock, zmq.POLLIN)

		send_msg(exp_sock, self.mtool.fill_msg("start_experiment"))
		reply =  self._poll_recv(exp_sock, 20000)
		self.poller.unregister(exp_sock)
		return reply

	def force_kill_experiment(self, strname):
		pass

	def get_experiment_contact(self, strname):
		send_msg(self.server_req_socket, self.mtool.fill_msg("get_experiment_contact",
										strname=strname))
		response = self._poll_recv(self.server_req_socket, self.default_timeout)
		return response


	def ping_server(self, timeout=50):
		send_msg(self.server_req_socket, self.mtool.fill_msg("ping"))
		response = self._poll_recv(self.server_req_socket, timeout)
		return response

	def retry_ping(self, timeout=50):
		response = self._poll_recv(self.server_req_socket, timeout)
		return response


	def _poll_recv(self, socket, timeout):
		try:
			socks = dict(self.poller.poll(timeout=timeout))
		except zmq.ZMQError, e:
			print "obci_client: zmq.poll(): " + e.strerror
			return None

		if socket in socks and socks[socket] == zmq.POLLIN:
			return self.mtool.unpack_msg(recv_msg(socket))
		else:
			return None

	def send_create_experiment(self, launch_file=None, sandbox_dir=None):

		send_msg(self.server_req_socket, self.mtool.fill_msg("create_experiment",
							launch_file=launch_file, sandbox_dir=sandbox_dir))

		response = self._poll_recv(self.server_req_socket, 5000)
		return response

	def send_list_experiments(self):
		send_msg(self.server_req_socket, self.mtool.fill_msg("list_experiments"))

		response = self._poll_recv(self.server_req_socket, 2000)
		return response

	def get_experiment_details(self, strname, peer_id=None):
		response = self.get_experiment_contact(strname)

		if response.type == "rq_error":
			return response

		sock = self.ctx.socket(zmq.REQ)
		for addr in response.rep_addrs:
			sock.connect(addr)
		self.poller.register(sock, zmq.POLLIN)

		send_msg(sock, self.mtool.fill_msg("get_experiment_info", peer_id=peer_id))
		response = self._poll_recv(sock, 2000)
		self.poller.unregister(sock)
		return response

	def kill_exp(self, strname, force=False):
		send_msg(self.server_req_socket,
				self.mtool.fill_msg("kill_experiment", strname=strname))
		return self._poll_recv(self.server_req_socket, 2000)
