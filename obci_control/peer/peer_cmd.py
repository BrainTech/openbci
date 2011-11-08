#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse

import peer_config_control
from common.config_helpers import LOCAL_PARAMS, EXT_PARAMS, CONFIG_SOURCES,\
							PEER_CONFIG_SECTIONS, LAUNCH_DEPENDENCIES

import common.obci_control_settings


class PeerCmd(object):
	def __init__(self):
		self.parser = argparse.ArgumentParser(usage="%(prog)s peer_id [options]")
		self.configure_argparser()

	def configure_argparser(self):

		self.parser.add_argument('peer_id',
									help="Unique name for this instance of this module")

		if common.obci_control_settings.USE_ZMQ:
			self.parser.add_argument('rep_sock', help="Socket address for incoming requests")

		self.parser.add_argument('-p', '--'+LOCAL_PARAMS,
									nargs=2,
									action=PeerParamAction,
									help="[param_name value] Local parameter override value.",
									type=str)
		self.parser.add_argument('-e', '--'+EXT_PARAMS, nargs=2, action=ExtParamAction,
									help="[param_name value] External parameter override value.")


		self.parser.add_argument('-c', '--'+CONFIG_SOURCES, nargs=2, action=ConfigSourceAction,
									help="[src_name module_id] Config source ID assignment")
		self.parser.add_argument('-d', '--'+LAUNCH_DEPENDENCIES, nargs=2, action=LaunchDepAction,
									help="[dep_name module_id] Launch dependency ID assignment")

		self.parser.add_argument('-f', '--config_file', type=path_to_file, action='append',
									help="[path_to_file] Additional configuration file (overrides).")
		self.parser.add_argument('--wait-config', action='store_true',
									help="Wait for init configuration message.")

	def parse_cmd(self):
		args = self.parser.parse_args()

		config_overrides = {}
		other_params = {}

		for attr, val in vars(args).iteritems():
			if attr in PEER_CONFIG_SECTIONS:
				config_overrides[attr] = val if val is not None else {}
			else:
				other_params[attr] = val

		return config_overrides, other_params

class PeerParamAction(argparse.Action):
	def __call__(self, parser, namespace, values, option_string=None):
		par, value = values[0], values[1]
		dic = getattr(namespace, self.dest)
		if dic is None:
			dic = {}
		dic[par] = value
		setattr(namespace, self.dest, dic)

class ExtParamAction(PeerParamAction):
	pass

class ConfigSourceAction(PeerParamAction):
	pass

class LaunchDepAction(PeerParamAction):
	pass

def path_to_file(string):
	if not os.path.exists(string):
		msg = "{} -- path not found!".format(string)
		raise argparse.ArgumentTypeError(msg)
	return string

if __name__ == "__main__":
	print PeerCmd().parse_cmd()