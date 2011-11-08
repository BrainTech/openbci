#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import argparse

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates
import common.net_tools as net

from obci_control_peer import OBCIControlPeer, basic_arg_parser

class OBCIExperiment(OBCIControlPeer):

	def __init__(self, obci_install_dir, sandbox_dir, launch_file=None,
										source_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_experiment'):

		self.sandbox_dir = sandbox_dir
		self.launch_file = launch_file
		self.supervisors = {}

		self.running = False
		super(OBCIExperiment, self).__init__(obci_install_dir,
											source_addresses,
											rep_addresses,
											pub_addresses,
											name)


	def start_obci_supervisor(self):
		superv = OBCIProcessSupervisor(self.addresses,
										self.obci_install_dir, 'process_supervisor')



if __name__ == '__main__':

	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
					description='Create, launch and manage an OBCI experiment.')
	parser.add_argument('--sandbox-dir',
	                   help='Directory to store temporary and log files')
	parser.add_argument('--launch-file',
	                   help='Experiment launch file')
	parser.add_argument('--name', default='obci_experiment',
	                   help='Human readable name of this process')

	args = parser.parse_args()
	print vars(args)

#	exp = OBCIExperiment( ['tcp://*:22233'], '/host/dev/openbci',
#							'~/.obci', None, 'obci_exp')
	exp = OBCIExperiment(args.obci_dir, args.sandbox_dir,
							args.launch_file, args.sv_addresses,
							args.rep_addresses, args.pub_addresses, args.name)


	exp.run()
