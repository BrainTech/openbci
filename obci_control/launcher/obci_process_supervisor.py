#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import subprocess
import argparse

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates
import common.net_tools as net

from obci_control_peer import OBCIControlPeer, basic_arg_parser

class OBCIProcessSupervisor(OBCIControlPeer):
	def __init__(self, obci_install_dir, source_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_process_supervisor'):

		self.peers = {}
		self.obci_instance = None
		super(OBCIProcessSupervisor, self).__init__(obci_install_dir,
														None, rep_addresses,
														  pub_addresses,
														  name)

	def start_peer(self, peer_state):
		pass

	def kill_peer(self, peer_state):
		pass

	def start_instance(self):
		pass

	def kill_instance(self, wipe_logs=True):
		pass

	def restart_instance(self, wipe_logs=True):
		self.kill_instance(obci_inst_state, wipe_logs)
		self.start_instance(obci_inst_state)


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
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()])
	parser.add_argument('--name', default='obci_process_supervisor',
	                   help='Human readable name of this process')
	args = parser.parse_args()
	print args
	process_sv = OBCIProcessSupervisor(args.obci_dir, args.sv_addresses,
							args.rep_addresses, args.pub_addresses, args.name)
	process_sv.run()