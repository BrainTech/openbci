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
import common.obci_control_settings as settings

from obci_control_peer import OBCIControlPeer, basic_arg_parser
import launcher_tools

class OBCIProcessSupervisor(OBCIControlPeer):

	def __init__(self, obci_install_dir, sandbox_dir,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_process_supervisor'):

		self.peers = {}
		self.status = launcher_tools.ExperimentStatus()
		self.source_pub_addresses = source_pub_addresses
		self.ip = net.ext_ip()
		self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR


		super(OBCIProcessSupervisor, self).__init__(obci_install_dir,
											source_addresses=source_addresses,
											rep_addresses=rep_addresses,
											pub_addresses=pub_addresses,
											name=name)

	def peer_type(self):
		return "obci_process_supervisor"

	def net_init(self):
		self.source_sub_socket = self.ctx.socket(zmq.SUB)
		self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

		if self.source_pub_addresses:
			for addr in self.source_pub_addresses:
				self.source_sub_socket.connect(addr)


		super(OBCIProcessSupervisor, self).net_init()

	def params_for_registration(self):
		return dict(pid=os.getpid(), machine=self.ip)

	def custom_sockets(self):
		return [self.source_sub_socket]

	def start_instance(self):
		pass

	def kill_instance(self, wipe_logs=True):
		pass

	def restart_instance(self, wipe_logs=True):
		self.kill_instance(obci_inst_state, wipe_logs)
		self.start_instance(obci_inst_state)




class SysPeerStatus(launcher_tools.PeerStatus):
	def __init__(self, peer_id):
		pass

def process_supervisor_arg_parser():
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
					description='A process supervisor for OBCI Peers')
	parser.add_argument('--sv-pub-addresses', nargs='+',
					help='Addresses of the PUB socket of the supervisor')
	parser.add_argument('--sandbox-dir',
					help='Directory to store temporary and log files')

	parser.add_argument('--name', default='obci_process_supervisor',
					help='Human readable name of this process')
	return parser


if __name__ == '__main__':
	parser = process_supervisor_arg_parser()
	args = parser.parse_args()

	process_sv = OBCIProcessSupervisor(args.obci_dir, args.sandbox_dir,
							source_addresses=args.sv_addresses,
							source_pub_addresses=args.sv_pub_addresses,
							rep_addresses=args.rep_addresses,
							pub_addresses=args.pub_addresses,
							name=args.name)
	process_sv.run()