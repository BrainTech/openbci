#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import subprocess

import zmq

from common.obci_control_settings import PORT_RANGE
from obci_controller_messages import fill_msg, decode_msg

class OBCIMachine(object):

	def __init__(self, address, obci_install_dir, controller_addr,
												name='obci_machine'):

		self.address = address
		self.obci_dir = obci_install_dir
		self.controller_addr = controller_addr
		self.uuid = str(uuid.uuid4())
		self.name = name
		self.peers = {}
		self.obci_instances = {}

		self.ctx = zmq.Context()

	def net_init(self):
		self.server = self.ctx.socket(zmq.REP)
		rep_port = self.server.bind_to_random_port(self.address,
											min_port=PORT_RANGE[0],
											max_port=PORT_RANGE[1])

		self.publish = self.ctx.socket(zmq.PUB)
		pub_port = self.publish.bind_to_random_port(self.address,
										min_port=PORT_RANGE[0],
										max_port=PORT_RANGE[1])

		self.client = self.ctx.socket(zmq.REQ)
		self.client.connect(self.controller_addr)

		self._register_machine(rep_port, pub_port)

	def _register_machine(self, rep_port, pub_port):
		message = fill_msg("register_machine", uuid=self.uuid,
												address=self.address,
												rep_port=rep_port,
												pub_port=pub_port,
												name=self.name,
												main=True)
		self._send_msg(self.client, message)
		response_str = self._recv_msg(self.client)
		response = decode_msg(response_str)
		print response
		if response["type"] == "error":
			print "BLE"
			sys.exit(2)


	def start_peer(self, peer_state):
		pass

	def kill_peer(self, peer_state):
		pass

	def start_instance(self, obci_inst_state):
		pass

	def kill_instance(self, obci_inst_state, wipe_logs=True):
		pass

	def restart_instance(self, obci_inst_state, wipe_logs=True):
		self.kill_instance(obci_inst_state, wipe_logs)
		self.start_instance(obci_inst_state, wipe_logs)

	def _send_msg(self, sock, message):
		return sock.send_unicode(message)

	def _recv_msg(self, sock):
		return sock.recv_unicode()

# Process states

NOT_RUNNING = 0 # process hasn't started yet
RUNNING = 1     # process is running
FINISHED = 2    # process exited normally
FAILED = 3      # process exited with error

PEER_STATES_BASIC = [NOT_RUNNING, RUNNING, FINISHED, FAILED]

class SysPeerState(object):

	def __init__(self, peer_id, peer_uuid, obci_inst_state,
										peer_path, peer_args=None):

		self.peer_id = peer_id
		self.peer_uuid = peer_uuid
		self.obci_inst = obci_inst_state
		self.path = peer_path
		self.peer_init_args = peer_args
		self.pid = None
		self.log_file = None
		self.process_state = NOT_RUNNING
		self.return_code = None

class SysOBCIInstanceState(object):

	def __init__(self, uuid, log_dir, main_machine, launch_file=None):
		self.uuid = uuid
		self.log_dir = log_dir
		self.launch_file = launch_file
		self.main_machine = main_machine


if __name__ == '__main__':
	machine = OBCIMachine('tcp://127.0.0.1', '/host/dev/openbci', 'tcp://127.0.0.1:23456')
	machine.net_init()