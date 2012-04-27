#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import os
import warnings
import codecs
import io
import json

import peer.peer_config as peer_config
import peer.peer_config_serializer as peer_config_serializer
from launcher.system_config import OBCIExperimentConfig, OBCISystemConfigError
from launcher_tools import expand_path, default_config_path
from launch_file_parser import parse_peer_default_config
import common.obci_control_settings as settings
import launcher_tools
PEERS = "peers"
CONFIG_SRCS = "config_sources"
LAUNCH_DEPS = "launch_dependencies"
SYS_SECTIONS = [PEERS]

class LaunchFileSerializer(object):

    def serialize(self, system_config, dump_dir_path, dump_file):
        self._init_tools()
        if dump_dir_path:
            dump_dir_path = os.path.realpath(dump_dir_path)
            if dump_dir_path and not os.path.exists(dump_dir_path):
                os.mkdir(dump_dir_path)
        self._prepare(system_config, dump_file)
        self._dump_special_sections(system_config, dump_file)
        self._dump_peer_configs(system_config, dump_file, dump_dir_path)
        self._save(dump_file, dump_dir_path)

    def _init_tools(self):
        raise NotImplementedError()

    def _prepare(self, system_config, dump_file):
        raise NotImplementedError()

    def _dump_special_sections(self, system_config, dump_file):
        raise NotImplementedError()

    def _dump_peer_configs(self, system_config, dump_file, dump_dir):
        raise NotImplementedError()

    def _dump_peer(self, peer_config, dump_file, dump_dir):
        raise NotImplementedError()

    def _save(self, dump_file, dump_dir_path):
        raise NotImplementedError()

class LaunchFileSerializerINI(LaunchFileSerializer):
    """
    Dump scenario to an INI scenario file and separate peer config files.
    """

    def _init_tools(self):
        self.parser = ConfigParser.RawConfigParser()
        self.parser.add_section(PEERS)

    def _prepare(self, system_config, dump_file):
        pass

    def _dump_special_sections(self, system_config, dump_file):
        self.parser.set(PEERS, "scenario_dir", system_config.scenario_dir)


    def _dump_peer_configs(self, system_config, dump_file, dump_dir):
        for peer, descriptor in system_config.peers.iteritems():
            peer_section = PEERS + "." + peer
            self.parser.add_section(peer_section)
            self.parser.set(peer_section, "path", descriptor.path)

            peer_file_name = self._dump_peer(descriptor, dump_file, dump_dir)

            if peer_file_name is not None:
                if peer_file_name.startswith(os.environ['HOME']):
                    peer_file_name = peer_file_name.replace(os.environ['HOME'], '~')
                self.parser.set(peer_section, "config", peer_file_name)

            self._dump_peer_config_sources(peer, descriptor.config.config_sources)
            self._dump_peer_launch_deps(peer, descriptor.config.launch_deps)

    def _dump_peer_config_sources(self, peer_id, config_sources):
        if config_sources:
            conf_section = PEERS + "." + peer_id + "." + CONFIG_SRCS
            self.parser.add_section(conf_section)
            for src_name, src in config_sources.iteritems():
                self.parser.set(conf_section, src_name, src)

    def _dump_peer_launch_deps(self, peer_id, launch_deps):
        if launch_deps:
            conf_section = PEERS + "." + peer_id + "." + LAUNCH_DEPS
            self.parser.add_section(conf_section)
            for dep_name, dep in launch_deps.iteritems():
                self.parser.set(conf_section, dep_name, dep)

    def _dump_peer(self, peer_descriptor, dump_file, dump_dir):
        ser = peer_config_serializer.PeerConfigSerializerINI()
        base_config, parser = parse_peer_default_config(peer_descriptor.peer_id,
                                                        peer_descriptor.path)
        diff_src, diff_deps, diff_params = ser.difference(base_config, peer_descriptor.config)
        peer_file_name = None

        if diff_src or diff_deps or diff_params:
            peer_file_name = os.path.join(dump_dir, peer_descriptor.peer_id + '.ini')
            with codecs.open(peer_file_name, "w", "utf-8") as f:
                ser.serialize_diff(base_config, peer_descriptor.config, f)
        return peer_file_name

    def _save(self, p_file_obj, dump_dir):
        self.parser.write(p_file_obj)



class LaunchFileSerializerJSON(LaunchFileSerializer):
    """
    Dump entire scenario to one large JSON.
    """
    def __init__(self):
        self.dic = {}

    def _init_tools(self):
        self.dic = {PEERS : {}}

    def _prepare(self, system_config, dump_file):
        pass

    def _dump_special_sections(self, system_config, dump_file):
        self.dic[PEERS]["scenario_dir"] = system_config.scenario_dir

    def _dump_peer_configs(self, system_config, dump_file, dump_dir):
        for peer, descriptor in system_config.peers.iteritems():
            peer_cfg = self.dic[PEERS][peer] = {}
            peer_cfg["path"] = descriptor.path

            peer_json = self._dump_peer(descriptor, dump_file, dump_dir)

            peer_cfg["config"] = json.loads(peer_json)

            self._dump_peer_config_sources(peer, descriptor.config.config_sources)
            self._dump_peer_launch_deps(peer, descriptor.config.launch_deps)

    def _dump_peer(self, peer_descriptor, dump_file, dump_dir):
        ser = peer_config_serializer.PeerConfigSerializerJSON()
        base_config, parser = parse_peer_default_config(peer_descriptor.peer_id,
                                                        peer_descriptor.path)
        diff_src, diff_deps, diff_params = ser.difference(base_config, peer_descriptor.config)

        conf = '{}'
        if diff_src or diff_deps or diff_params:
            buf = io.BytesIO()
            ser.serialize_diff(base_config, peer_descriptor.config, buf)
            conf = unicode(buf.getvalue())
        return conf

    def _dump_peer_config_sources(self, peer_id, config_sources):
        if config_sources:
            conf_section = self.dic[PEERS][peer_id][CONFIG_SRCS] = {}
            for src_name, src in config_sources.iteritems():
                conf_section[src_name] = src

    def _dump_peer_launch_deps(self, peer_id, launch_deps):
        if launch_deps:
            conf_section = self.dic[PEERS][peer_id][LAUNCH_DEPS] = {}
            for dep_name, dep in launch_deps.iteritems():
                conf_section[dep_name] = dep

    def _save(self, p_file_obj, dump_dir=None):
        json.dump(self.dic, p_file_obj)

def serialize_scenario_json(p_system_config):
    buf = io.BytesIO()
    ser = LaunchFileSerializerJSON()
    ser.serialize(p_system_config, None, buf)
    return unicode(buf.getvalue())

if __name__ == '__main__':
    import launch_file_parser
    import system_config

    launch_parser = launch_file_parser.LaunchFileParser(
                            launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
    config = system_config.OBCIExperimentConfig()
    status = launcher_tools.ExperimentStatus()
    with open(launcher_tools.expand_path('scenarios/cebit/switch/hci_switch_mult_dummy.ini')) as f:
        launch_parser.parse(f, config)
    rd, details = config.config_ready()
    print rd, details
    print "INFO A"
    print config.all_param_values('amplifier')
    print "\n *********************************\n"
    json_ser = serialize_scenario_json(config)
    print json_ser

    jsonpar = launch_file_parser.LaunchJSONParser(
                        launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
    inbuf = io.BytesIO(json_ser.encode(encoding='utf-8'))
    new_conf = system_config.OBCIExperimentConfig()

    jsonpar.parse(inbuf, new_conf)
    rd, details = new_conf.config_ready()
    print "INFO B"
    print rd, details
    print new_conf.all_param_values('amplifier')