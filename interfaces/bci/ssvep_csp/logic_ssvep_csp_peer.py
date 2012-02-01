#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings
from acquisition import acquisition_helper
from interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis

from logic import logic_logging as logger
LOGGER = logger.get_logger("ssvep_csp", 'info')

class LogicSsvepCsp(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicSsvepCsp, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CSP)
        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        self.data_file_name = acquisition_helper.get_file_path(f_dir, f_name)

        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        self.csp_file_name = acquisition_helper.get_file_path(f_dir, f_name)

        self.use_channels=None
        tmp = self.config.get_param("use_channels")
        if len(tmp) > 0:
            self.use_channels = tmp.split(';')

        self.ignore_channels=None
        tmp = self.config.get_param("ignore_channels")
        if len(tmp) > 0:
            self.ignore_channels = tmp.split(';')

        self.ears_channels=None
        tmp = self.config.get_param("ears_channels")
        if len(tmp) > 0:
            self.ears_channels = tmp.split(';')

        run_on_start = int(self.config.get_param("run_on_start"))
        self.ready()
        
        if run_on_start:
            self.run()
        else:
            self._data_finished = False
            self._info_finished = False
            self._tags_finished = False

    def _all_ready(self):
        return self._data_finished and self._info_finished and self._tags_finished

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_SAVER_FINISHED:
            self._data_finished = True
        elif mxmsg.type == types.INFO_SAVER_FINISHED:
            self._info_finished = True
        elif mxmsg.type == types.TAG_SAVER_FINISHED:
            self._tags_finished = True
        else:
            LOGGER.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.run()

    def run(self):
        logic_ssvep_csp_analysis.run(
            self.data_file_name,
            self.csp_file_name,
            self.use_channels,
            self.ignore_channels,
            self.ears_channels)
        sys.exit(0)

if __name__ == "__main__":
    LogicSsvepCsp(settings.MULTIPLEXER_ADDRESSES).loop()


        
