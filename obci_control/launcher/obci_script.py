#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import json
import time
import subprocess
import sys

import launcher_tools
launcher_tools.update_obci_syspath()
launcher_tools.update_pythonpath()

import obci_server
import obci_client
import common.obci_control_settings as settings

class OpenBCICmd(object):
	def __init__(self):
		self.parser = argparse.ArgumentParser(description="Launch and manage OBCI experiments,\
 their state and configuration", epilog="(c) 2011, Warsaw University", prog='obci')
		self.configure_argparser()

	def configure_argparser(self):
		subparsers = self.parser.add_subparsers(title='available commands',
		description='(use %(prog)s *command* -h for help on a specific command)')

		parser_srv = subparsers.add_parser('srv',
					help="Start OBCIServer")

		parser_launch = subparsers.add_parser('launch',
					help="Launch an OpenBCI system with configuration \
specified in a launch file or in a newly created Experiment")

		parser_launch.add_argument('file', type=path_to_file,
					help="OpenBCI launch configuration (experiment configuration).")


		parser_add = subparsers.add_parser('add',
					help="Add a peer to an experiment launch configuration")

		parser_new = subparsers.add_parser('new',
					help="Create a new experiment launch configuration")

		parser_kill = subparsers.add_parser('kill',
					help="Kill an OpenBCI experiment")

		parser_killall = subparsers.add_parser('killall',
					help="Kill everything: all experiments and OBCI server.")

		parser_join = subparsers.add_parser('join',
					help="Join a running OpenBCI experiment with a new peer.")

		parser_config = subparsers.add_parser('config',
					help="View or change a single peer configuration")

		parser_save = subparsers.add_parser('save',
					help="Save OBCI experiment configuration to a launch file or save\
							a peer configuration")

		parser_info = subparsers.add_parser('info',
					help="Get information about controlled OpenBCI experiments\
							and peers")




	def parse_cmd(self):
		args = self.parser.parse_args()
		return args

def server_rep_addresses():
	directory = os.path.abspath(settings.DEFAULT_SANDBOX_DIR)
	if not os.path.exists(directory):
		os.mkdir(directory)

	filename = settings.SERVER_CONTACT_NAME
	fpath = os.path.join(directory, filename)
	if os.path.exists(fpath):
		with open(fpath) as f:
			return json.load(f)
	else:
		return None

def server_prep():
	if server_rep_addresses() is None:
		success = launch_obci_server()
		if not success:
			print "Could not launch OBCI Server"
			sys.exit(1)
		print "OBCI server launched. PID: {0}".format(success.pid)

	tries = 30
	addrs = server_rep_addresses()
	while addrs is None and tries:
		time.sleep(0.05)
		tries -= 1
		addrs = server_rep_addresses()

	if addrs is None:
		print "Could not obtain OBCI Server Addresses"
		sys.exit(1)
	else:
		return addrs

def launch_obci_server():
	path = obci_server.__file__
	path = '.'.join([path.rsplit('.', 1)[0], 'py'])
	srv = subprocess.Popen([path])
	return srv

def path_to_file(string):
	if not os.path.exists(string):
		msg = "{0} -- path not found!".format(string)
		raise argparse.ArgumentTypeError(msg)
	return string


if __name__ == "__main__":

	OpenBCICmd().parse_cmd()
	addrs = server_prep()