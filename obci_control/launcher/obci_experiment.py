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

import launch_file_parser
import launcher_tools
import system_config

class OBCIExperiment(OBCIControlPeer):

	def __init__(self, obci_install_dir, sandbox_dir, launch_file=None,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_experiment',
										launch=False):

		super(OBCIExperiment, self).__init__(obci_install_dir,
											source_addresses,
											rep_addresses,
											pub_addresses,
											name)


		self.sandbox_dir = sandbox_dir
		self.launch_file = launch_file
		self.exp_config = system_config.OBCIExperimentConfig(uuid=self.uuid)
		self.supervisors = {}

		self.running = False
		self.source_pub_addresses = source_pub_addresses

		if not self.make_experiment_config():
			print "DUPA"

	def start_obci_supervisor(self):
		superv = OBCIProcessSupervisor(self.addresses,
										self.obci_install_dir, 'process_supervisor')

	def make_experiment_config(self):
		launch_parser = launch_file_parser.LaunchFileParser(launcher_tools.obci_root())
		try:
			with open(self.launch_file) as f:
				launch_parser.parse(f, self.exp_config)
		except:
			return False

		print self.exp_config
		return True

	def peer_type(self):
		return 'obci_experiment'

	def handle_get_experiment_info(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('experiment_info',
											exp_info=self.exp_config.info()))

	def handle_get_peer_config(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('pong'))


	def handle_start_experiment(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('pong'))



def experiment_arg_parser():
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
					description='Create, launch and manage an OBCI experiment.')
	parser.add_argument('--sv-pub-addresses', nargs='+',
					help='Addresses of the PUB socket of the supervisor')
	parser.add_argument('--sandbox-dir',
					help='Directory to store temporary and log files')
	parser.add_argument('--launch-file',
					help='Experiment launch file')
	parser.add_argument('--name', default='obci_experiment',
					help='Human readable name of this process')
	parser.add_argument('--launch', default=False,
	                   help='Launch the experiment specified in launch file')


	return parser

if __name__ == '__main__':



	args = experiment_arg_parser().parse_args()
	print vars(args)

#	exp = OBCIExperiment( ['tcp://*:22233'], '/host/dev/openbci',
#							'~/.obci', None, 'obci_exp')
	exp = OBCIExperiment(args.obci_dir, args.sandbox_dir,
							args.launch_file, args.sv_addresses, args.sv_pub_addresses,
							args.rep_addresses, args.pub_addresses, args.name,
							args.launch)


	exp.run()
