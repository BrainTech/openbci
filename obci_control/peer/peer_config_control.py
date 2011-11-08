#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import codecs
import inspect
import io
import json

import peer_config
import peer_config_parser
import peer_config_serializer
from peer_cmd import PeerCmd

from common.config_helpers import *

import common.config_message
import config_control_io

import settings

CONFIG_FILE_EXT = 'ini'
WAIT_CONFIG = "wait_config"
CONFIG_FILE = "config_file"
PEER_ID = "peer_id"

class PeerControl(object):

	def __init__(self, p_peer=None, param_processing_method=None,
							   param_change_trigger_method=None):
		self.core = peer_config.PeerConfig()
		self.peer = p_peer
		self.peer_process_param = param_processing_method
		self.peer_param_trigger = param_change_trigger_method

		self.cmd_overrides = {}
		self.file_list = []
		self.wait_config = False

		self.peer_id = None

		self.io = None

		self.ready_peers = {}

		self._handlers = {
			'SET_CONFIG' : self._handle_set_config,
			'GET_CONFIG' : self._handle_get_config,

			'GET_PARAMS' : self._handle_get_params,
			'PARAM_VALUES' : self._handle_param_values,
			'PEER_READY' : self._handle_peer_ready,
			'PEER_CONFIG_ALL' : self._handle_unsupported_message,
			'PEER_CONFIG' : self._handle_unsupported_message
		}

	def initialize_config(self):
		self.process_cmd()
		self.load_config_base()
		for filename in self.file_list:
			self._load_config_from_file(filename, CONFIG_FILE_EXT, update=True)
		dictparser = peer_config_parser.parser('python')
		dictparser.parse(self.cmd_overrides, self.core, update=True)


		self.io = config_control_io.PeerConfigMx(
										settings.MULTIPLEXER_ADDRESSES, self)

		self.request_ext_params()

		# msg = common.config_message.ConfigMessage()
		# msg.sender = self.peer_id
		# msg.receiver = ''
		# msg.type = 'CONFIG_READY'
		# self.io.send_msg(msg.pack())


	def synchronize(self, event):
		pass


	def process_cmd(self):
		cmd_ovr, other_params = PeerCmd().parse_cmd()
		self.peer_id = self.core.peer_id = other_params[PEER_ID]
		if other_params[CONFIG_FILE] is not None:
			self.file_list = other_params[CONFIG_FILE]
		self.cmd_overrides = cmd_ovr
		if other_params[WAIT_CONFIG]:
			self.wait_config = True


	def load_config_base(self):
		if self.peer is None:
			raise NoPeerError

		peer_file = inspect.getfile(self.peer.__init__)
		base_name = peer_file.rsplit('.', 1)[0]
		base_config_path = '.'.join([base_name, CONFIG_FILE_EXT])
		print base_config_path

		self._load_config_from_file(base_config_path, CONFIG_FILE_EXT)


	def _load_config_from_file(self, p_path, p_type, update=False):
		with open(p_path) as f:
			parser = peer_config_parser.parser(p_type)
			parser.parse(f, self.core)


	def handle_config_message(self, p_msg):
		print p_msg
		if p_msg.type not in self._handlers:
			return self._handle_unsupported_message(p_msg)

		return self._handlers[p_msg.type](p_msg)


	def param(self, p_name):
		return self.core.get_param(p_name)

	def set_param(self, p_name, p_value):
		return self.core.update_local_param(p_name, p_value)

	def get_params(self, p_param_names):
		pass


	def _handle_set_config(self, p_msg):
		jsonparser = peer_config_parser.parser('json')
		jsonparser.parse(io.BytesIO(p_msg.message), self.core, update=True)


	def _handle_get_config(self, p_msg):
		pass

	def _handle_get_params(self, p_msg):
		params = json.loads(p_msg.message)
		data = {}
		print self.core
		print "GET ", params
		for param in params:
			data[param] = self.core.get_param(param)
		resp = common.config_message.ConfigMessage()
		resp.type = 'PARAM_VALUES'
		resp.sender = self.peer_id
		resp.receiver = p_msg.sender
		resp.message = json.dumps(data)
		return resp.pack()

	def _handle_param_values(self, p_msg):
		params = json.loads(p_msg.message)
		#TODO check sender id and if params is a dict
		for par, val in params.iteritems():
			self.core.set_param_from_source(p_msg.sender, par, val)

	def _handle_peer_ready(self, p_msg):
		pass
		# src_names = self.core.source_ids[p_msg.sender]

		# for name in src_names:
		# 	if name in self._wait_peers:
		# 		self._wait_peers.remove(name)

	def _handle_unsupported_message(self, p_msg):
		warnings.warn(UnsupportedMessageType())
		return None


	def request_ext_params(self):
		msg = common.config_message.ConfigMessage()
		msg.type = 'GET_PARAMS'
		msg.sender = self.peer_id

		def _unset_param_count():
			return reduce(lambda x, y: x + y,
							[len(self.core.unset_params_for_source(src)) \
								for src in self.core.used_config_sources()], 0)

		while not self.core.config_ready():
			for src in self.core.used_config_sources():
				params = self.core.unset_params_for_source(src).keys()

				msg.receiver = self.core.config_sources[src]
				msg.message = json.dumps(params)
				print "requesting: {0}".format(msg)
				self.io.request_once(msg.pack())
			print "{0} external params still unset".format(_unset_param_count())

		print self.core


#todo message verification


class PeerConfigControlError(Exception):
	pass

class NoPeerError(PeerConfigControlError):
	pass

class PeerConfigControlWarning(Warning):
	pass

class UnsupportedMessageType(PeerConfigControlWarning):
	pass