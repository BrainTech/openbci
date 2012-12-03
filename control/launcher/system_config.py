#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
import os
import codecs
import logging

from obci.control.common.config_helpers import *
import obci.control.launcher.launcher_tools as launcher_tools
from obci.control.peer.peer_config_serializer import PeerConfigSerializerCmd
from obci.control import peer
import obci.control.peer.peer_config_parser as peer_config_parser
from obci.control.peer.peer_config import PeerConfig

from obci.control.common.graph import Graph, Vertex

class OBCIExperimentConfig(object):
    def __init__(self, launch_file_path=None, uuid=None, 
                                    origin_machine=None, logger=None):
        self.uuid = uuid
        self.launch_file_path = launch_file_path


        self.origin_machine = origin_machine if origin_machine else ''
        self.scenario_dir = ''
        self.mx = 0
        self.peers = {}
        self.logger = logger or logging.getLogger("ObciExperimentConfig")

    @property
    def launch_file_path(self):
        return self._launch_file_path

    @launch_file_path.setter
    def launch_file_path(self, path):
        self._launch_file_path = path
        if path:
            self._launch_file_path = launcher_tools.obci_root_relative(path)


    def peer_config(self, peer_id):
        return self.peers[peer_id].config

    def update_local_param(self, peer_id, p_name, p_value):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        return self.peers[peer_id].config.update_local_param(p_name, p_value)

    def update_external_param(self, peer_id, p_name, src, src_param):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        return self.peers[peer_id].config.update_external_param_def(p_name, src+'.'+src_param)

    def update_peer_config(self, peer_id, config_dict):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        conf = self.peers[peer_id].config
        dictparser = peer.peer_config_parser.parser('python')
        return dictparser.parse(config_dict, conf, update=True)

    def file_update_peer_config(self, peer_id, file_path):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        parser = peer.peer_config_parser.parser('ini')
        with open(file_path) as f:
            return parser.parse(f, self.peers[peer_id].config, update=True)

    def peer_path(self, peer_id):
        return self.peers[peer_id].path

    def peer_machine(self, peer_id):
        return self.peers[peer_id].machine

    def update_peer_machine(self, peer_id, machine_ip):
        self.peers[peer_id].machine = machine_ip

    def extend_with_peer(self, peer_id, peer_path, peer_cfg, 
                                            config_sources=None, launch_deps=None, 
                                            param_overwrites=None, machine=None):
        override = peer_id in self.peers
        machine = machine or ""

        self.add_peer(peer_id)

        self.set_peer_config(peer_id, peer_cfg)
        self.set_peer_path(peer_id, peer_path)
        self.set_peer_machine(peer_id, machine)

        if config_sources:
            for src_name, src_id in config_sources.iteritems():
                self.set_config_source(peer_id, src_name, src_id)
        else:
            for src in peer_cfg.config_sources:
                if src in self.peers:
                    self.set_config_source(peer_id, src, src)

        if launch_deps:            
            for dep_name, dep_id in launch_deps.iteritems():
                self.set_launch_dependency(peer_id, dep_name, dep_id)
        else:
            for dep in peer_cfg.launch_deps:
                if dep in self.peers:
                    self.set_launch_dependency(peer_id, dep, dep)

        if param_overwrites:
            for par, val in param_overwrites.iteritems():
                self.update_local_param(peer_id, par, val)
            
        return override

    def add_peer(self, peer_id):
        self.peers[peer_id] = PeerConfigDescription(peer_id, self.uuid)

    def set_peer_config(self, peer_id, peer_config):
        self.peers[peer_id].config = peer_config

    def set_peer_path(self, peer_id, path):
        self.peers[peer_id].path = path

    def set_config_source(self, peer_id, src_name, src_peer_id):
        if src_peer_id and src_peer_id not in self.peers:
            raise OBCISystemConfigError("(src) Peer ID {0} not in peer list".format(src_peer_id))
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        if self.peers[peer_id] is None:
            raise OBCISystemConfigError("Configuration for peer ID {0} does not exist".format(peer_id))

        self.peers[peer_id].config.set_config_source(src_name, src_peer_id)

    def set_launch_dependency(self, peer_id, dep_name, dep_peer_id):
        if dep_peer_id not in self.peers:
            raise OBCISystemConfigError("(dep) Peer ID {0} not in peer list".format(dep_peer_id))
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        if self.peers[peer_id] is None:
            raise OBCISystemConfigError("Configuration for peer ID {0} does not exist".format(peer_id))

        self.peers[peer_id].config.set_launch_dependency(dep_name, dep_peer_id)

    def set_peer_machine(self, peer_id, machine_name):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
        self.peers[peer_id].machine = machine_name

    def all_param_values(self, peer_id):

        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))

        config = self.peers[peer_id].config
        not_fresh = config.param_values
        vals = {}
        for key in not_fresh:
            vals[key] = self._param_value(peer_id, key, config)
        return vals

    def local_params(self, peer_id):
        return self.peers[peer_id].config.local_params

    def param_value(self, peer_id, param_name):
        if peer_id not in self.peers:
            raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))

        config = self.peers[peer_id].config
        return self._param_value(peer_id, param_name, config)

    def _param_value(self, peer_id, param_name, config):
        if param_name in config.local_params:
            return config.local_params[param_name]
        elif param_name in config.ext_param_defs:
            peer, param = config.ext_param_defs[param_name]
            source = config.config_sources[peer]
            return self.param_value(source, param)
        else:
            raise OBCISystemConfigError("Param {0} does not exist in {1}".format(param_name, peer_id))

    def config_ready(self):
        details = {}

        if not self.peers:
            return False, details

        for peer_state in self.peers.values():
            if not peer_state.ready(details):
                return False, details

        res, det = self.launch_deps_graph_ok()
        if not res:
            return res, det
        res, det = self.config_sources_graph_ok()
        if not res:
            return res, det

        return True, {}

    def launch_deps_graph_ok(self):
        gr = self.peer_graph('list_launch_deps')
        res, order = gr.topo_sort()
        details = '' if res else {'desc': "Launch dependencies graph contains a cycle!!!"}
        return res, details

    def config_sources_graph_ok(self):
        gr = self.peer_graph('list_config_sources')
        res, order = gr.topo_sort()
        details = '' if res else {'desc': "Config sources graph contains a cycle!!!"}
        return res, details

    def status(self, status_obj):
        ready, details = self.config_ready()
        st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

        status_obj.set_status(st, details=details)
        #TODO details, e.g. info about cycles

        for peer_id in self.peers:
            pst = status_obj.peers_status[peer_id] = launcher_tools.PeerStatus(peer_id)
            self.peers[peer_id].status(pst)

    def peer_machines(self):
        machines = set([self.origin_machine])
        for peer in self.peers.values():
            if peer.machine:
                machines.add(peer.machine)
        return list(machines)

    def launch_data(self, peer_machine):
        ldata = {}

        for peer in self.peers.values():
            machine = peer.machine if peer.machine else self.origin_machine
            if machine == peer_machine:
                ldata[peer.peer_id] = peer.launch_data()
        return ldata


    def peer_graph(self, neighbours_method):
        gr = Graph(bidirectional=False)
        vs ={}
        for p in self.peers.values():
            # print "vertices: ", vs
            meth = getattr(p, neighbours_method)
            ngs = meth()
            # print "$$$$$$$$$$$$$$$$$$", p.peer_id, ngs, neighbours_method
            # print p.config
            if not p in vs:
                # print "create vertex for ", p.peer_id,
                ver_p = Vertex(gr, p)
                vs[p] = ver_p
                gr.add_vertex(ver_p)
                # print "vvvv:    ", gr.vertices()
            for ne in ngs:
                pr = self.peers[ne]
                if not pr in vs:
                    # print "create second vertex for", pr.peer_id,
                    ver_ng = Vertex(gr, pr)
                    vs[pr] = ver_ng
                    gr.add_vertex(ver_ng)
                    # print "vvvvvv2  ", gr.vertices()
                gr.add_edge(vs[p], vs[pr])
                # print "vvvvv after edge:   ", ver_p, ver_ng, "::::", gr.vertices()
        return gr

    def _topo_sort(self, neighbours_method):
        gr = self.peer_graph(neighbours_method)
        res, order = gr.topo_sort()
        ret_order = []
        for part in order:
            ret_order.append([v._model.peer_id for v in part])
        return ret_order

    def peer_order(self):
        order = self._topo_sort('list_launch_deps')
        if order:
            part1 = order[0]
            if 'mx' in part1:
                part1.remove('mx')
            if 'config_server' in part1:
                part1.remove('config_server')
            order = [['mx'],['config_server']] + order
        return order


    def peers_info(self):
        peers = {}
        for p in self.peers:
            peers[p] = self.peers[p].info()
        return peers

    def info(self):
        exp = {}
        exp["uuid"] = self.uuid
        exp["origin_machine"] = self.origin_machine
        exp["launch_file_path"] = self.launch_file_path
        peers = self.peers_info()
        exp["peers"] = peers
        return exp




class PeerConfigDescription(object):
    def __init__(self, peer_id, experiment_id, config=None, path=None, machine=None,
                        logger=None):
        self.peer_id = peer_id

        self.experiment_id = experiment_id

        self.config = PeerConfig(peer_id)
        self.path = path
        self.machine = machine
        self.public_params = []
        self.logger = logger or logging.getLogger("ObciExperimentConfig.peer_id")
        self.del_after_stop = False

    def __str__(self):
        return self.peer_id

    def ready(self, details=None):
        loc_det = {}
        ready = self.config is not None and \
                self.path is not None and\
                self.machine is not None and\
                self.peer_id is not None

        if not ready:
            return ready
        ready = self.config.config_sources_ready(loc_det) and ready
        ready = self.config.launch_deps_ready(loc_det) and ready
        if details is not None:
            details[self.peer_id] = loc_det
        return ready

    def list_config_sources(self):
        return [val for val in self.config.config_sources.values() if\
                    val in self.config.used_config_sources()]

    def list_launch_deps(self):
        return self.config.launch_deps.values()

    def status(self, peer_status_obj):
        det = {}
        ready = self.ready(det)
        st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

        peer_status_obj.set_status(st, details=det)

    def peer_type(self):
        if self.peer_id.startswith('mx'):
            return 'multiplexer'
        else:
            return 'obci_peer'

    def launch_data(self):
        ser = PeerConfigSerializerCmd()
        args = [self.peer_id]
        peer_parser = peer.peer_config_parser.parser("ini")
        base_config = PeerConfig(self.peer_id)
        conf_path = launcher_tools.default_config_path(self.path)
        if conf_path:

            with codecs.open(conf_path, "r", "utf8") as f:
                self.logger.info("parsing default config for peer %s, %s ",
                                                         self.peer_id, conf_path)
                peer_parser.parse(f, base_config)

        ser.serialize_diff(base_config, self.config, args)

        return dict(peer_id=self.peer_id, experiment_id=self.experiment_id,
                    path=self.path, machine=self.machine,
                    args=args, peer_type=self.peer_type())


    def info(self, detailed=False):
        info = dict(peer_id=self.peer_id,
                    path=self.path, machine=self.machine, peer_type=self.peer_type()
                    )

        if not self.config:
            return info

        info[CONFIG_SOURCES] = self.config.config_sources
        info[LAUNCH_DEPENDENCIES] = self.config.launch_deps

        if detailed:
            info[LOCAL_PARAMS] = self.config.local_params
            info[EXT_PARAMS] = self.config.ext_param_defs
        return info



class OBCISystemConfigError(Exception):
    pass


class OBCISystemConfigWarning(Warning):
    pass
