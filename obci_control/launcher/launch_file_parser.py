#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import os
import warnings

import peer.peer_config as peer_config
import peer.peer_config_parser as peer_config_parser
from launcher.system_config import OBCIExperimentConfig, OBCISystemConfigError

PEERS = "peers"
CONFIG_SRCS = "config_sources"
SYS_SECTIONS = [PEERS]

class LaunchFileParser(object):

	def __init__(self, obci_base_dir):
		self.base_dir = obci_base_dir
		self.parser = None
		self.config = None

	def parse(self, p_file, p_config_obj):
		self._prepare(p_file, p_config_obj)
		self._do_parse()
		return True

	def _prepare(self, p_file, p_config_obj):
		self.parser = ConfigParser.RawConfigParser()
		self.parser.readfp(p_file)
		self.config = p_config_obj

	def _do_parse(self):
		self._check_sections()
		self._load_general_settings()
		peer_sections = self.__peer_sections()

		self._load_peer_ids(peer_sections)
		self._load_launch_data(peer_sections)
		self._set_sources()

		#for peer_sec in peer_sections:
		#	print self.config.peers[self.__peer_id(peer_sec)].config


	def _check_sections(self):
		for section in self.parser.sections():
			main_s = self.__main_section(section)
			if main_s not in SYS_SECTIONS:
				raise OBCISystemConfigError("Unrecognized launch file section: {0}".format(main_s))

	def _load_general_settings(self):
		items = self.parser.items(PEERS)
		if self.parser.has_option(PEERS, 'mx'):
			self.config.mx = self.parser.get(PEERS, 'mx')
		if self.parser.has_option(PEERS, 'scenario_dir'):
			self.config.scenario_dir = self.parser.get(PEERS, 'scenario_dir')

	def _load_peer_ids(self, peer_sections):
		for section in peer_sections:
			peer_id = self.__peer_id(section)
			self.config.add_peer(peer_id)


	def _load_launch_data(self, peer_sections):
		for sec in peer_sections:
			self._load_peer(sec)

	def _load_peer(self, peer_section):
		peer_id = self.__peer_id(peer_section)
		items = self.parser.items(peer_section)
		machine_set= False

		for (param, value) in items:
			if param == "path":
				#self.config.set_peer_path(peer_id, os.path.join(self.base_dir, value))
				self.config.set_peer_path(peer_id, value)
			elif param == "config":
				if self.config.scenario_dir:
					warnings.warn("Choosing {0} for {1} config\
 instead of a file in scenario dir {2}!!!".format(value, peer_id, self.config.scenario_dir))
				self._parse_peer_config(peer_id, value)
			elif param == "machine":
				machine_set = True
				self._set_peer_machine(peer_id, value)
			else:
				raise OBCISystemConfigError("Unrecognized launch file option {0}".format(param))
		if not machine_set:
			self._set_peer_machine(peer_id, '')
		if not self.config.peers[peer_id].config:
			config_file = os.path.join(self.config.scenario_dir, peer_id + '.ini')

	def _parse_peer_config(self, peer_id, config_path):
		peer_parser = peer_config_parser.parser("ini")
		peer_cfg = peer_config.PeerConfig(peer_id)
		with open(config_path) as f:
			peer_parser.parse(f, peer_cfg)
			self.config.set_peer_config(peer_id, peer_cfg)


	def _set_sources(self):
		for src_sec in self.__config_src_sections():
			for src_name, src_id in self.parser.items(src_sec):
				self.config.set_config_source(self.__peer_id(src_sec),
												src_name,
												src_id)

	def _set_peer_machine(self, peer_id, machine_name):
		self.config.set_peer_machine(peer_id, machine_name)

	def __peer_id(self, conf_section):
		return conf_section.split('.')[1]

	def __main_section(self, conf_section):
		return conf_section.split('.', 1)[0]

	def __peer_sections(self):
		return [sec for sec in self.parser.sections() if \
								sec.startswith(PEERS + '.') and \
								len(sec.split('.')) == 2]

	def __config_src_sections(self):
		return [sec for sec in self.parser.sections() if
								sec.startswith(PEERS + '.') and \
								sec.endswith(CONFIG_SRCS)]