# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import copy
import info_file_proxy
import signal_logging as logger
import signal_exceptions
LOGGER = logger.get_logger("read_info_source", "info")

class InfoSource(object):
    def get_param(self, p_key):
        LOGGER.error("The method must be subclassed")
    def get_params(self):
        LOGGER.error("The method must be subclassed")
    def set_params(self, p_params):
        LOGGER.error("The method must be subclassed")
    def update_params(self, p_params):
        LOGGER.error("The method must be subclassed")
    def set_param(self, k, v):
        LOGGER.error("The method must be subclassed")
    def reset_params(self):
        LOGGER.error("The method must be subclassed")        
    def __deepcopy__(self, memo):
        return MemoryInfoSource(copy.deepcopy(self.get_params()))


class MemoryInfoSource(InfoSource):
    def __init__(self, p_params={}):
        self._params = None
        self.set_params(p_params)
    def set_params(self, p_params):
        self._params = dict(p_params)

    def reset_params(self):
        self.set_params({})

    def update_params(self, p_params):
        for k, v in p_params.iteritems():
            self.set_param(k, v)

    def set_param(self, p_key, p_value):
        self._params[p_key] = p_value

    def get_param(self, p_key):
        try:
            return self._params[p_key]
        except KeyError:
            raise signal_exceptions.NoParameter(p_key)

    def get_params(self):
        return self._params

class FileInfoSource(InfoSource):
    def __init__(self, p_file):
        self._memory_source = None
        try:
            ''+p_file
            LOGGER.debug("Got file path.")
            self._info_proxy = info_file_proxy.InfoFileReadProxy(p_file)
        except TypeError:
            LOGGER.debug("Got file proxy.")
            self._info_proxy = p_file


    def get_param(self, p_key):
        if self._memory_source is None:
            return self._info_proxy.get_param(p_key)
        else:
            return self._memory_source.get_param(p_key)

    def get_params(self):
        if self._memory_source is None:
            return self._info_proxy.get_params()
        else:
            return self._memory_source.get_params()
    
    def _get_memory_source(self):
        if self._memory_source is None:
            self._memory_source = MemoryInfoSource(self._info_proxy.get_params())
        return self._memory_source

    def set_param(self, k, v):
        self._get_memory_source().set_param(k, v)
    def set_params(self, p_params):
        self._get_memory_source().set_params(p_params)
    def update_params(self, p_params):
        self._get_memory_source().update_params(p_params)
    def reset_params(self):
        self._get_memory_source().reset_params()
