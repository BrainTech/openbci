#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings
from acquisition import acquisition_helper
from gui.ugm import ugm_helper
from interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper

from logic import logic_logging as logger
LOGGER = logger.get_logger("ssvep_csp", 'info')

class LogicSsvepCsp(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicSsvepCsp, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CSP)
        self.use_channels=None
        tmp = self.config.get_param("use_channels")
        if len(tmp) > 0:
            self.use_channels = tmp.split(';')

        self.ignore_channels=None
        tmp = self.config.get_param("ignore_channels")
        if len(tmp) > 0:
            self.ignore_channels = tmp.split(';')

        self.montage = self.config.get_param("montage")

        tmp = self.config.get_param("montage_channels")
        if len(tmp) > 0:
            self.montage_channels = tmp.split(';')
        else:
            self.montage_channels = []

        self.run_offline = int(self.config.get_param("run_offline"))
        self.ready()
        
        if self.run_offline:
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
        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        cfg = logic_ssvep_csp_analysis.run(
            acquisition_helper.get_file_path(f_dir, f_name),
            self.use_channels,
            self.ignore_channels,
            self.montage,
            self.montage_channels)

        if not self.run_offline:
            self._show_configs(cfg)
            self._edit_configs(cfg)

        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)

        if not self.run_offline:
            self._run_next_scenario()

    def _show_configs(self, cfg):
        text_id = int(self.config.get_param('ugm_text_id'))
        all_freqs = cfg['all_freqs'].split(';')
        all_means = cfg['all_means'].split(';')
        ugm_helper.send_config_for(
            self.conn, text_id, 'message',
            u''.join([u"Czestosci od najlepszej do najgorszej:"# i ich sila:",
                     '\n',
                     #' '.join([all_freqs[i]+" ("+all_means[i]+")" for i in range(len(all_freqs))]),
                      ' '.join([all_freqs[i] for i in range(len(all_freqs))]),
                     '\n',
                     u'Proponowany rozmiar bufora: '+str(cfg['buffer'])+" sekund",
                     '\n',
                     u'Nizej mozesz zmienic proponowane wartosci:'
                     ])
            )

    def _edit_configs(self, cfg):
        buffer = float(cfg['buffer'])
        freqs = [int(i) for i in cfg['freqs'].split(';')]
        LOGGER.info("Configs before edit:")
        LOGGER.info("Buffer: "+str(buffer)+" freqs: "+str(freqs))
        buffer, freqs = ssvep_csp_helper.edit_csp_configs(buffer, freqs)
        cfg['buffer'] = buffer
        cfg['freqs'] = ';'.join([str(i) for i in freqs])
        LOGGER.info("Configs after edit:")
        LOGGER.info("Buffer: "+str(buffer)+" freqs: "+str(freqs))


    def _run_next_scenario(self):
        path = self.config.get_param('next_scenario_path')
        if len(path) > 0:
            os.system("sleep 5 && obci kill ss && sleep 10 && obci launch "+path+" &")
        else:
            LOGGER.info("NO NEXT SCENARIO!!! Finish!!!")
            sys.exit(0)

if __name__ == "__main__":
    LogicSsvepCsp(settings.MULTIPLEXER_ADDRESSES).loop()


        
