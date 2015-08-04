#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os, time
import random

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings
from obci.acquisition import acquisition_helper
from obci.gui.ugm import ugm_helper
from obci.analysis.mgr_ssvep.compute_calibration import ComputeCalibration
from obci.interfaces.bci.ssvep_csp import ssvep_csp_helper
from obci.logic import logic_helper
from obci.utils import tags_helper
from obci.utils import context as ctx
from obci.utils.openbci_logging import log_crash



class LogicSsvepCsp(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(LogicSsvepCsp, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CSP)
        self.all_channels=None
        tmp = self.config.get_param("all_channels")
        if len(tmp) > 0:
            self.all_channels = tmp.split(';')

        self.channels_to_ignore=None
        tmp = self.config.get_param("channels_to_ignore")
        if len(tmp) > 0:
            self.channels_to_ignore = tmp.split(';')

        self.channels_to_leave=None
        tmp = self.config.get_param("channels_to_leave")
        if len(tmp) > 0:
            self.channels_to_leave = tmp.split(';')

        self.montage = self.config.get_param("montage")

        tmp = self.config.get_param("montage_channels")
        if len(tmp) > 0:
            self.montage_channels = tmp.split(';')
        else:
            self.montage_channels = []

        self.l_trial = float(self.config.get_param("l_trial"))
        self.l_pattern = float(self.config.get_param("l_pattern"))
        self.l_train = float(self.config.get_param("l_train"))
        self.l_buffer_trenning = float(self.config.get_param("l_buffer_trenning"))

        self.freq_to_train=None
        tmp = self.config.get_param("freq_to_train")
        if len(tmp) > 0:
            self.freq_to_train = [int(f) for f in tmp.split(';')]

        self.active_field = int(self.config.get_param('active_field'))+4
        self.tag_name = self.config.get_param('target_tag_name')

        self.mode = self.config.get_param("mode")
        self.ready()
        
        if self.mode == 'offline':
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
            self.logger.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.run()

    def run(self):
        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        f_name_output = self.config.get_param("csp_file_name")
        f_dir_output = self.config.get_param("csp_file_path")

        analysis = ComputeCalibration(f_name, f_dir,                  
                                      f_dir_output,
                                      f_name_output,
                                      l_trial=self.l_trial, 
                                      ignore_channels=self.channels_to_ignore,
                                      montage_type=self.montage, 
                                      montage_channels=self.montage_channels, 
                                      leave_channels=self.channels_to_leave, 
                                      tag_name=self.tag_name, 
                                      freq_to_train=self.freq_to_train, 
                                      active_field=self.active_field,
                                      l_pattern=self.l_pattern,
                                      l_train=self.l_train,
                                      l_buffer_trenning=self.l_buffer_trenning)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        cfg = analysis.run()

        self.finish(cfg)

    def finish(self, cfg):
        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        self._shuffle_freqs(cfg)
        if self.mode == 'offline':
            ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
        elif self.mode == 'manual':
            self._show_configs(cfg, suffix=self.config.get_param('propose_freqs_text'))
            self._send_csp_info(cfg)
            ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
            self._run_next_scenario()
        else:
            self.logger.warning("Unrecognised mode: "+self.mode)

    def _shuffle_freqs(self, cfg):
   
        if self.config.get_param('shuffle_freqs') == '0':
            return

        elif self.config.get_param('shuffle_freqs') == '1':
             #Move second best freq to the last field...
            freqs = [int(i) for i in cfg['freq'].split(';')]
            new_freqs = []
            new_freqs.append(freqs[0])
            for f in freqs[3:]:
                new_freqs.append(f)
            new_freqs.append(freqs[2])
            new_freqs.append(freqs[1])

        elif self.config.get_param('shuffle_freqs') == 'random':
            new_freqs = [int(i) for i in cfg['freq'].split(';')]
            random.shuffle(new_freqs)
        
        cfg['freq'] = ';'.join([str(i) for i in new_freqs])
        
    def _show_configs(self, cfg, suffix=u""):
        text_id = int(self.config.get_param('ugm_text_id'))
        all_freqs = cfg['freq'].split(';')
        ugm_helper.send_config_for(
            self.conn, text_id, 'message',
            u''.join([self.config.get_param('show_freqs_text'),# i ich sila:,
                     '\n',
                     #' '.join([all_freqs[i]+" ("+all_means[i]+")" for i in range(len(all_freqs))]),
                      ' '.join([all_freqs[i] for i in range(len(all_freqs))]),
                     #'\n',
                     #u'Suggested buffer length: '+str(cfg['buffer'])+" secs",
                     '\n',
                     suffix
                     ])
            )

    def _send_csp_info(self, cfg):
        desc = dict(cfg)
        t = time.time()
        tags_helper.send_tag(
            self.conn, t, t, 
            "cspInfo",
            desc)

    def _run_next_scenario(self):
        self._run_scenario(self.config.get_param('next_scenario_path'))
        
    def _run_prev_scenario(self):
        self._run_scenario(self.config.get_param('prev_scenario_path'))

    def _run_scenario(self, path):
        if len(path) > 0:
            logic_helper.restart_scenario(self.conn, path,
                                          leave_on=['amplifier'])
        else:
            self.logger.info("NO NEXT SCENARIO!!! Finish!!!")
            sys.exit(0)

        

if __name__ == "__main__":
    LogicSsvepCsp(settings.MULTIPLEXER_ADDRESSES).loop()


        
