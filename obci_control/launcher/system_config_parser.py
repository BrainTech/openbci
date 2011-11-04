#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser

import peer.peer_config
import peer.peer_config_parser
from launcher.system_config import OBCISystemConfig, OBCISystemConfigError

PEERS = "peers"
CONFIG_SRCS = "config_sources"
SYS_SECTIONS = [PEERS]

class SystemConfigParser(object):

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

		print self.parser.sections()

		peer_sections = self.__peer_sections()

		self._load_peer_ids(peer_sections)

		self._load_configs(peer_sections)

		self._set_sources(peer_sections)


	def _check_sections(self):
		for section in self.parser.sections():
			main_s = self.__main_section(section)
			if main_s not in SYS_SECTIONS:
				raise OBCISystemConfigError

	def _load_peer_ids(self, peer_sections):
		for section in peer_sections:
			peer_id = self.__peer_id(section)
			self.config.add_peer(peer_id)


	def _load_configs(self, peer_sections):
		for sec in peer_sections:
			self._load_peer_config(sec)

	def _load_peer_config(self, peer_section):
		peer_id = self.__peer_id(peer_section)
		items = self.parser.items(peer_section)
		for (param, value) in items:
			if param == "path":
				self.config.set_peer_path(peer_id, value)
			elif param == "config":
				peer_parser = peer_config_parser.parser("ini")
				peer_cfg = peer_config.PeerConfig(peer_id)
				with open(self.base_dir + '/' + value) as f:
					peer_parser.parse(f, peer_cfg)
					self.config.set_peer_config(peer_id, peer_cfg)
					print self.config.peers[peer_id].config
			elif param == "machine":
				pass



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