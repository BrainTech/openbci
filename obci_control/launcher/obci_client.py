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

	def __init__(self, server_addresses, zmq_context=None):
		self.ctx = zmq_context if zmq_context else zmq.Context()

		self.server_req_socket = self.ctx.socket(zmq.REQ)
		for addr in addresses:
			self.server_req_socket.connect(addr)



	def send_create_experiment(self, launch_file=None):
		pass