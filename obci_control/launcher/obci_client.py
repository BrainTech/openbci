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

	default_timeout=200

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

		if result.type != "experiment_created":
			return result

		start_result = self.send_start_experiment(result.rep_addrs)

	def send_start_experiment(self, exp_addrs):
		exp_sock = self.ctx.socket(zmq.REQ)
		for addr in exp_addrs:
			exp_sock.connect(addr)

		send_msg(exp_sock, self.mtool.fill_msg("start_experiment"))

	def ping_server(self, timeout=50):
		send_msg(self.server_req_socket, self.mtool.fill_msg("ping"))
		return self._poll_recv(self.server_req_socket, timeout)

	def retry_ping(self, timeout=50):
		return self._poll_recv(self.server_req_socket, timeout)


	def _poll_recv(self, socket, timeout):
		try:
			socks = dict(self.poller.poll(timeout=timeout))
		except zmq.ZMQError, e:
			print "obci_client: zmq.poll(): " + e.strerror
			return None

		if socket in socks and socks[socket] == zmq.POLLIN:
			return recv_msg(socket)
		else:
			return None

	def send_create_experiment(self, launch_file=None, sandbox_dir=None):

		send_msg(self.server_req_socket, self.mtool.fill_msg("create_experiment",
							launch_file=launch_file, sandbox_dir=sandbox_dir))

		enc_msg = recv_msg(self.server_req_socket)
		message = self.mtool.unpack_msg(enc_msg)
		return message

	def send_list_experiments(self):
		send_msg(self.server_req_socket, self.mtool.fill_msg("list_experiments"))

		response = recv_msg(self.server_req_socket)
		return self.mtool.unpack_msg(response)

	def send_get_experiment_info(self, exp_rep_addr):
		if self.exp_req_socket is None:
			self.exp_req_socket = self.ctx.socket(zmq.REQ)
			for addr in exp_rep_addr:
				self.exp_req_socket.connect(addr)

		send_msg(self.exp_req_socket, self.mtool.fill_msg("get_experiment_info"))
		response = recv_msg(self.exp_req_socket)
		return self.mtool.unpack_msg(response)