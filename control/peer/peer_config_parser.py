#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import json
import io


import peer.peer_config as pc
import obci.control.common.config_helpers as helpers



class PeerConfigParser(object):

    config_parts = [
        helpers.CONFIG_SOURCES,
        helpers.EXT_PARAMS,
        helpers.LOCAL_PARAMS,
        helpers.LAUNCH_DEPENDENCIES
        ]

    def parse(self, p_file, p_config_obj, update=False):
        self._prepare(p_file, p_config_obj, update)
        self._do_parse()
        return True

    def _prepare(self, p_file, p_config_obj, update=False):
        raise NotImplemented

    def _do_parse(self):
        self._check_sections()
        self._parse_config_sources()
        self._parse_external_params()
        self._parse_local_params()
        self._parse_launch_dependencies()

    def check_complete(self, p_config):
        return p_config.check()

    def _get_config_sources(self):
        raise NotImplemented

    def _parse_config_sources(self):
        if not self._check_has_section(helpers.CONFIG_SOURCES):
            return

        sources = self._get_config_sources()
        for name, val in sources:
            self._check_source(name, val)
            val = '' if val == None else val
            self.config.set_config_source(name, val)

    def _get_launch_dependencies(self):
        raise NotImplemented

    def _parse_launch_dependencies(self):
        if not self._check_has_section(helpers.LAUNCH_DEPENDENCIES):
            return
        sources = self._get_launch_dependencies()
        for name, val in sources:
            self._check_source(name, val)
            val = '' if val == None else val
            self.config.set_launch_dependency(name, val)

    def _get_external_params(self):
        raise NotImplemented

    def _parse_external_params(self):
        if not self._check_has_section(helpers.EXT_PARAMS):
            return

        exts = self._get_external_params()
        for name, val in exts:
            if self.update:
                self.config.update_external_param_def(name, val)
            else:
                self.config.add_external_param_def(name, val)

    def _get_local_params(self):
        raise NotImplemented

    def _parse_local_params(self):
        if not self._check_has_section(helpers.LOCAL_PARAMS):
            return

        exts = self._get_local_params()
        for name, val in exts:
            v = '' if val == None else val
            if self.update:
                self.config.update_local_param(name, v)
            else:
                self.config.add_local_param(name, v)


    def _check_has_section(self, name):
        pass

    def _get_sections(self):
        raise NotImplemented

    def _check_sections(self):
        sections = self._get_sections()

        for sec in sections:
            if not sec in self.config_parts:
                raise UnknownConfigSection(err_illegal_sec_name.format(sec))

        return True

    def _check_source(self, src_name, value):
        if value is not None and value != '' and self.update == False:
            raise ConfigSourceError(err_config_source.format(src_name, value))
        return True



class PeerConfigParserINI(PeerConfigParser):

    def __init__(self):
        self.parser = None
        self.config = None
        self.update = False

    def _prepare(self, p_file, p_config_obj, update=False):
        self.parser = ConfigParser.RawConfigParser()
        self.parser.readfp(p_file)
        self.config = p_config_obj
        self.update = update

    def _get_config_sources(self):
        return self.parser.items(helpers.CONFIG_SOURCES)

    def _get_external_params(self):
        return self.parser.items(helpers.EXT_PARAMS)

    def _get_local_params(self):
        return self.parser.items(helpers.LOCAL_PARAMS)

    def _get_launch_dependencies(self):
        return self.parser.items(helpers.LAUNCH_DEPENDENCIES)

    def _check_has_section(self, name):
        if self.parser.has_section(name):
            return True
        else:
            #if not self.update:
            #    raise IncompleteConfigSections(err_no_section.format(name))
            #else:
            return False

    def _get_sections(self):
        return self.parser.sections()


class PeerConfigParserJSON(PeerConfigParser):
    def __init__(self):
        self.load = None
        self.config = None
        self.update = False

    def _prepare(self, p_file, p_config_obj, update=False):
        self.load = json.load(p_file)
        if not isinstance(self.load, dict):
            raise ValueError("Expected a JSON'd dictionary!")

        self.config = p_config_obj
        self.update = update

        for key in [helpers.CONFIG_SOURCES, helpers.LAUNCH_DEPENDENCIES,\
                        helpers.LOCAL_PARAMS, helpers.EXT_PARAMS]:
            if self.load[key] is None:
                self.load[key] = {}

    def _get_config_sources(self):
        return [(key, val) for (key, val) in \
                    self.load[helpers.CONFIG_SOURCES].iteritems()]

    def _get_launch_dependencies(self):
        return [(key, val) for (key, val) in \
                    self.load[helpers.LAUNCH_DEPENDENCIES].iteritems()]

    def _get_external_params(self):
        return [(key, val) for (key, val) in \
                    self.load[helpers.EXT_PARAMS].iteritems()]

    def _get_local_params(self):
        return [(key, val) for (key, val) in \
                    self.load[helpers.LOCAL_PARAMS].iteritems()]


    def _check_has_section(self, name):
        if self.load.has_key(name):
            return True
        else:
            # if not self.update:
            #     raise IncompleteConfigSections(err_no_section.format(name))
            # else:
            return False

    def _get_sections(self):
        return self.load.keys()

class PeerConfigParserDict(PeerConfigParserJSON):
    def __init__(self):
        self.load = None
        self.config = None
        self.update = False

    def _prepare(self, p_python_dict, p_config_obj, update=False):
        self.load = p_python_dict
        if not isinstance(self.load, dict):
            raise ValueError("Expected a dictionary!")

        for key in [helpers.CONFIG_SOURCES, helpers.LAUNCH_DEPENDENCIES,\
                        helpers.LOCAL_PARAMS, helpers.EXT_PARAMS]:
            if self.load[key] is None:
                self.load[key] = {}

        self.config = p_config_obj
        self.update = update


err_no_section = "Section '{0}' not found in config file."
err_config_source = "Config source definitions should not have \
values assigned in config file. Name: '{0}', illegal value: '{1}'."
err_illegal_sec_name = "Illegal section name: '{0}'"

class PeerConfigParserError(Exception):
    pass
    # def __init__(self, value=None):
    #     self.value = value

    # def __str__(self):
    #     if self.value is not None:
    #         return repr(self.value)
    #     else:
    #         return repr(self)

class ParserNotFoundError(PeerConfigParserError):
    pass

class ConfigSourceError(PeerConfigParserError):
    pass

class UnknownConfigSection(PeerConfigParserError):
    pass

class IncompleteConfigSections(PeerConfigParserError):
    pass

parsers = {
    'ini' : PeerConfigParserINI,
    'json': PeerConfigParserJSON,
    'python' : PeerConfigParserDict
}

def parser(parser_type):
    if parser_type not in parsers:
        raise ParserNotFoundError(parser_type)
    return parsers[parser_type]()
