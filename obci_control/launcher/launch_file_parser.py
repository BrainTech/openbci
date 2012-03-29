#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import os
import warnings
import codecs

import peer.peer_config as peer_config
import peer.peer_config_parser as peer_config_parser
from launcher.system_config import OBCIExperimentConfig, OBCISystemConfigError

PEERS = "peers"
CONFIG_SRCS = "config_sources"
LAUNCH_DEPS = "launch_dependencies"
SYS_SECTIONS = [PEERS]

class LaunchFileParser(object):

	def __init__(self, obci_base_dir, scenario_base_dir):
		self.base_dir = obci_base_dir
		self.scenario_dir = scenario_base_dir
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
		self._set_launch_deps()

		for peer_sec in peer_sections:
			#print self.config.peers[self.__peer_id(peer_sec)].config
			pass


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
			self.config.scenario_dir = self.__path(self.config.scenario_dir, base_dir=self.scenario_dir)
			#print "scenario dir: ", self.config.scenario_dir, self.scenario_dir

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
		peer_config_file = ''
		peer_path = ''

		for (param, value) in items:
			if param == "path":
				self.config.set_peer_path(peer_id, value)
				peer_path = self.config.peers[peer_id].path

			elif param == "config":
				if self.config.scenario_dir:
					warnings.warn("Choosing {0} for {1} config\
 instead of a file in scenario dir {2}!!!".format(value, peer_id, self.config.scenario_dir))
				peer_config_file = self.__path(value)
			elif param == "machine":
				machine_set = True
				self._set_peer_machine(peer_id, value)
			else:
				raise OBCISystemConfigError("Unrecognized launch file option {0}".format(param))
		if not machine_set:
			self._set_peer_machine(peer_id, '')
		if not peer_config_file:
			if self.config.scenario_dir:
				peer_config_file = os.path.join(self.config.scenario_dir, peer_id + '.ini')
			else:
				# well, then we'll try to load default .ini for this peer or,
				# if default config does not exist, leave config empty
				pass
		if not peer_path:
			raise OBCISystemConfigError("No program path defined for peer_id {0}".format(peer_id))

		self._parse_peer_config(peer_id, peer_config_file, peer_path)

	def __find_default_config_path(self, peer_program_path):
		#TODO move to ? obci main_config
		file_endings = ['py', 'java', 'jar', 'class', 'exe', 'sh', 'bin']
		base = peer_program_path
		sp = peer_program_path.rsplit('.', 1)
		if len(sp) > 1:
			if len(sp[1]) < 3 or sp[1] in file_endings:
				base = sp[0]
		conf_path = self.__path(base + '.ini')
		if os.path.exists(conf_path):
			return conf_path
		else: return ''

	def __path(self, path, base_dir=None):
		if base_dir is None:
			base_dir = self.base_dir
		if not path:
			return path

		p = os.path.expanduser(path)
		if os.path.isabs(p):
			return p
		else:
			return os.path.realpath(os.path.join(base_dir, p))

	def __parse_peer_default_config(self, peer_id, peer_program_path):
		#print "Trying to find default config for {0}, path: {1}".format(
		#											peer_id, peer_program_path)
		peer_parser = peer_config_parser.parser("ini")
		peer_cfg = peer_config.PeerConfig(peer_id)
		conf_path = self.__find_default_config_path(peer_program_path)
		if conf_path:

			with codecs.open(conf_path, "r", "utf8") as f:
				print "parsing default config for peer  ", peer_id, conf_path
				peer_parser.parse(f, peer_cfg)
			#print "Loaded default config {0} for {1}, path: {2}".format(
			#							conf_path, peer_id, peer_program_path)
		else:
			#print "No default config found for {1}, prog.path: {1}".format(
			#										peer_id, peer_program_path)
			pass
		return peer_cfg, peer_parser

	def _parse_peer_config(self, peer_id, config_path, peer_program_path):
		peer_cfg, peer_parser = self.__parse_peer_default_config(
												peer_id, peer_program_path)
		#print "Trying to parse {0} for {1}".format(config_path, peer_id)
		if config_path:
			with codecs.open(config_path, "r", "utf8") as f:
				print "parsing _custom_ config for peer  ", peer_id, config_path
				peer_parser.parse(f, peer_cfg)
		self.config.set_peer_config(peer_id, peer_cfg)


	def _set_sources(self):
		for src_sec in self.__config_src_sections():
			for src_name, src_id in self.parser.items(src_sec):
				self.config.set_config_source(self.__peer_id(src_sec),
												src_name,
												src_id)

	def _set_launch_deps(self):
		for dep_sec in self.__launch_dep_sections():
			for dep_name, dep_id in self.parser.items(dep_sec):
				self.config.set_launch_dependency(self.__peer_id(dep_sec),
												dep_name,
												dep_id)

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

	def __launch_dep_sections(self):
		return [sec for sec in self.parser.sections() if
								sec.startswith(PEERS + '.') and \
								sec.endswith(LAUNCH_DEPS)]
