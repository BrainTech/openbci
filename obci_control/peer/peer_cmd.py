#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse

from common.config_helpers import LOCAL_PARAMS, EXT_PARAMS, CONFIG_SOURCES,\
							PEER_CONFIG_SECTIONS, LAUNCH_DEPENDENCIES

import common.obci_control_settings


class PeerCmd(object):
	def __init__(self):
		self.parser = argparse.ArgumentParser(usage="%(prog)s peer_id [options]")
		self.configure_argparser()

	def configure_argparser(self):

		self.parser.add_argument('peer_id',
									help="Unique name for this instance of this peer")

		self.parser.add_argument('-p', '--'+LOCAL_PARAMS,
									nargs=2,
									action=PeerParamAction,
									help="Local parameter override value: param_name, value.",
									type=str)
		self.parser.add_argument('-e', '--'+EXT_PARAMS, nargs=2, action=ExtParamAction,
									help="External parameter override value: param_name value .")


		self.parser.add_argument('-c', '--'+CONFIG_SOURCES, nargs=2, action=ConfigSourceAction,
									help="Config source ID assignment: src_name peer_id")
		self.parser.add_argument('-d', '--'+LAUNCH_DEPENDENCIES, nargs=2, action=LaunchDepAction,
									help="Launch dependency ID assignment: dep_name peer_id")

		self.parser.add_argument('-f', '--config_file', type=path_to_file, action='append',
									help="Additional configuration file (overrides): path_to_file.")
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