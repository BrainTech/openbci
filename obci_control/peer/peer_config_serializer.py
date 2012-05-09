#!/usr/bin/python

import json
import ConfigParser

import common.config_helpers as helpers

class PeerConfigSerializer(object):

    config_parts = [
        helpers.CONFIG_SOURCES,
        helpers.LAUNCH_DEPENDENCIES,
        helpers.EXT_PARAMS,
        helpers.LOCAL_PARAMS
    ]

    def serialize(self, p_config, p_file_obj):
        self._prepare(p_config)
        self._do_serialize(p_config)
        self._save(p_file_obj)

    def serialize_diff(self, p_base_config, p_config, p_file_obj):
        self._prepare(p_config)
        self._do_serialize_diff(p_base_config, p_config)
        self._save(p_file_obj)

    def _prepare(self, p_config):
        raise NotImplementedError()

    def _save(self, p_file_obj):
        raise NotImplementedError()

    def _do_serialize(self, p_config):

        self._serialize_config_sources(p_config.config_sources)
        self._serialize_launch_deps(p_config.launch_deps)
        self._serialize_local_params(p_config.param_values,
                                     p_config.ext_param_defs)
        self._serialize_ext_params(p_config.param_values,
                                    p_config.ext_param_defs)

    def difference(self, p_base_config, p_config):
        sources = {}
        for src, val in p_config.config_sources.iteritems():
            if src not in p_base_config.config_sources:
                sources[src] = val

        deps = {}
        for dep, val in p_config.launch_deps.iteritems():
            if dep not in p_base_config.launch_deps:
                deps[dep] = val

        params = {}
        for par, val in p_config.param_values.iteritems():
            if par not in p_base_config.param_values:
                params[par] = val
            elif val != p_base_config.param_values[par]:
                params[par] = val
        return sources, deps, params

    def _do_serialize_diff(self, p_base_config, p_config):
        sources, deps, params = self.difference(p_base_config, p_config)
        self._serialize_config_sources(sources)

        self._serialize_launch_deps(deps)

        self._serialize_local_params(params, p_config.ext_param_defs)
        self._serialize_ext_params(params, p_config.ext_param_defs)

    def _serialize_config_sources(self, p_sources):
        raise NotImplementedError()

    def _serialize_launch_deps(self, p_deps):
        raise NotImplementedError()

    def _serialize_ext_params(self, p_values, p_ext_param_defs):
        raise NotImplementedError()

    def _serialize_local_params(self, p_values, p_ext_param_defs):
        raise NotImplementedError()


class PeerConfigSerializerINI(PeerConfigSerializer):
    def __init__(self):
        self.parser = None

    def _prepare(self, p_config):
        self.parser = ConfigParser.RawConfigParser()
        for sec in self.config_parts:
            self.parser.add_section(sec)

    def _save(self, p_file_obj):
        self.parser.write(p_file_obj)

    def _serialize_config_sources(self, p_sources):
        for src in p_sources.keys():
            self.parser.set(helpers.CONFIG_SOURCES, src, '')

    def _serialize_launch_deps(self, p_deps):
        for src in p_deps.keys():
            self.parser.set(helpers.LAUNCH_DEPENDENCIES, src, '')

    def _serialize_ext_params(self, p_values, p_ext_param_defs):
        for name, value in p_values.iteritems():
            if name in p_ext_param_defs:
                (src, par) = p_ext_param_defs[name]
                val = src + '.' + par
                self.parser.set(helpers.EXT_PARAMS, name, val)

    def _serialize_local_params(self, p_values, p_ext_param_defs):
        for name, value in p_values.iteritems():
            if name not in p_ext_param_defs:
                self.parser.set(helpers.LOCAL_PARAMS, name, value)


class PeerConfigSerializerJSON(PeerConfigSerializer):
    def __init__(self):
        self.dic = {}

    def _prepare(self, p_config):
        self.dic = {}

    def _save(self, p_file_obj):
        json.dump(self.dic, p_file_obj)

    def _do_serialize_diff(self, p_base_config, p_config):
        sources, deps, params = self.difference(p_base_config, p_config)
        print "serializing diff of ", p_config.peer_id, "conf_src:",sources, "deps:", deps, "params:",params
        self._serialize_config_sources(p_config.config_sources)

        self._serialize_launch_deps(p_config.launch_deps)

        self._serialize_local_params(params, p_config.ext_param_defs)
        self._serialize_ext_params(params, p_config.ext_param_defs)

    def _serialize_config_sources(self, p_sources):
        self.dic[helpers.CONFIG_SOURCES] = {}
        for src in p_sources.keys():
            self.dic[helpers.CONFIG_SOURCES][src] = ''

    def _serialize_launch_deps(self, p_deps):
        self.dic[helpers.LAUNCH_DEPENDENCIES] = {}
        for dep in p_deps.keys():
            self.dic[helpers.LAUNCH_DEPENDENCIES][dep] = ''

    def _serialize_local_params(self, p_values, p_ext_param_defs):
        self.dic[helpers.LOCAL_PARAMS] = {}
        for name, value in p_values.iteritems():
            if name not in p_ext_param_defs:
                self.dic[helpers.LOCAL_PARAMS][name] = value

    def _serialize_ext_params(self, p_values, p_ext_param_defs):
        self.dic[helpers.EXT_PARAMS] = {}
        for name, value in p_values.iteritems():
            if name in p_ext_param_defs:
                (src, par) = p_ext_param_defs[name]
                self.dic[helpers.EXT_PARAMS][name] = src + '.' + par

class PeerConfigSerializerCmd(PeerConfigSerializer):
    def __init__(self):
        self.args = []

    def _prepare(self, p_config):
        self.args = []

    def _save(self, p_file_obj):
        #p_file_obj.write(str(self.args))
        #print self.args
        for a in self.args:
            p_file_obj.append(a)
        #p_file_obj = self.args

    def _do_serialize_diff(self, p_base_config, p_config):
        sources, deps, params = self.difference(p_base_config, p_config)
        self._serialize_config_sources(p_config.config_sources)

        self._serialize_launch_deps(p_config.launch_deps)

        self._serialize_local_params(params, p_config.ext_param_defs)
        self._serialize_ext_params(params, p_config.ext_param_defs)

    def _serialize_config_sources(self, p_sources):
        for sname, peer_id in p_sources.iteritems():
            self.args += [helpers.CS, sname, peer_id]

    def _serialize_launch_deps(self, p_deps):
        for sname, peer_id in p_deps.iteritems():
            self.args += [helpers.LD, sname, peer_id]

    def _serialize_local_params(self, p_values, p_ext_param_defs):
        for name, value in p_values.iteritems():
            if name not in p_ext_param_defs or value is not None:
                self.args += [helpers.LP, name, value]

    def _serialize_ext_params(self, p_values, p_ext_param_defs):
        for name, value in p_values.iteritems():
            if name in p_ext_param_defs and value is None:
                (src, par) = p_ext_param_defs[name]
                self.args += [helpers.EP, name, src + '.' + par]

#TODO?
class PeerConfigSerializerProtobuf(PeerConfigSerializer):
    pass