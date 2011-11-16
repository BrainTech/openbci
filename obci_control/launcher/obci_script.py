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

def cmd_srv(args):
	if server_rep_addresses() is not None:
		print "OBCI Server is already running."
	else: server_prep(argv())

def cmd_launch(args):
	server_prep(argv())


def cmd_new(args):
	pass

def cmd_join(args):
	pass

def cmd_kill(args):
	pass

def cmd_killall(args):
	pass

def cmd_add(args):
	pass

def cmd_save(args):
	pass

def cmd_log(args):
	pass

def cmd_config(args):
	pass

def cmd_info(args):
	pass

def obci_arg_parser():
	parser = argparse.ArgumentParser(description="Launch and manage OBCI experiments,\
their state and configuration", epilog="(c) 2011, Warsaw University", prog='obci')
	configure_argparser(parser)
	return parser

def configure_argparser(parser):
	subparsers = parser.add_subparsers(title='available commands',
	description='(use %(prog)s *command* -h for help on a specific command)',
	dest='command_name')

	parser_srv = subparsers.add_parser('srv',
				parents=[obci_server.server_arg_parser(add_help=False)],
				help="Start OBCIServer")
	parser_srv.set_defaults(func=cmd_srv)

	parser_launch = subparsers.add_parser('launch',
				help="Launch an OpenBCI system with configuration \
specified in a launch file or in a newly created Experiment")

	parser_launch.add_argument('file', type=path_to_file,
				help="OpenBCI launch configuration (experiment configuration).")
	parser_launch.set_defaults(func=cmd_launch)


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

def server_prep(args=[]):
	addrs = server_rep_addresses()
	if addrs:
		return addrs

	success = launch_obci_server(args)
	if not success:
		print "Could not launch OBCI Server"
		sys.exit(1)
	print "OBCI server launched. PID: {0}".format(success.pid)

	tries = 30

	while addrs is None and tries:
		time.sleep(0.05)
		tries -= 1
		addrs = server_rep_addresses()

	if addrs is None:
		print "Could not obtain OBCI Server Addresses"
		sys.exit(1)
	else:
		return addrs

def launch_obci_server(args=[]):
	path = obci_server.__file__
	path = '.'.join([path.rsplit('.', 1)[0], 'py'])
	srv = subprocess.Popen(['python', path] + list(args))
	return srv

def path_to_file(string):
	if not os.path.exists(string):
		msg = "{0} -- path not found!".format(string)
		raise argparse.ArgumentTypeError(msg)
	return string

def argv():
	return sys.argv[2:]


if __name__ == "__main__":

	args = obci_arg_parser().parse_args()
	args.func(args)