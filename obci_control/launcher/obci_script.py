#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse


class OpenBCICmd(object):
	def __init__(self):
		self.parser = argparse.ArgumentParser()
		self.configure_argparser()

	def configure_argparser(self):


		subparsers = self.parser.add_subparsers(help='sub-command help')

		parser_launch = subparsers.add_parser('launch',
					help="Launch an OpenBCI system with configuration\
specified in a launch file")

		parser_launch.add_argument('file', type=path_to_file,
					help="OpenBCI launch configuration (experiment configuration).")


		parser_add = subparsers.add_parser('add',
					help="Add a peer to a system launch configuration")

		parser_new = subparsers.add_parser('new',
					help="Create a new system launch configuration")

		parser_kill = subparsers.add_parser('kill',
					help="Kill a running OpenBCI system instance")

		parser_join = subparsers.add_parser('join',
					help="Join a running OpenBCI system with a new peer.")

		parser_config = subparsers.add_parser('config',
					help="View or change a single peer configuration")

		parser_save = subparsers.add_parser('save',
					help="Save OBCI system configuration to a launch file or save\
							a peer configuration")

		parser_info = subparsers.add_parser('info',
					help="Get information about controlled OpenBCI system instances\
							and peers")




	def parse_cmd(self):
		args = self.parser.parse_args()

		print args



def path_to_file(string):
	if not os.path.exists(string):
		msg = "{} -- path not found!".format(string)
		raise argparse.ArgumentTypeError(msg)
	return string


if __name__ == "__main__":

	OpenBCICmd().parse_cmd()