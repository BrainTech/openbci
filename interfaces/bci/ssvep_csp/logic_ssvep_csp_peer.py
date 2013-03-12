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
from obci.interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis
from obci.interfaces.bci.ssvep_csp import ssvep_csp_helper
from obci.logic import logic_helper
from obci.utils import tags_helper
from obci.utils import context as ctx

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
        dec_count = int(self.config.get_param("dec_count"))
        context = ctx.get_new_context()
        context['logger'] = self.logger
        cfg = logic_ssvep_csp_analysis.run(
            acquisition_helper.get_file_path(f_dir, f_name),
            self.use_channels,
            self.ignore_channels,
            self.montage,
            self.montage_channels,
            dec_count,
            self.mode in ['offline', 'manual'],
            context)

        maybe_buffer = self.config.get_param('buffer_len')
        if len(maybe_buffer) > 0:
            self.logger.info("Overwrite csp buffer len:"+str(cfg['buffer'])+"with from config:"+str(maybe_buffer))
            cfg['buffer'] = float(maybe_buffer)

        self.finish(cfg)
    def finish(self, cfg):
        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")

        if self.mode == 'offline':
            ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
        elif self.mode == 'always_pass':
            self._determine_means(cfg)#for debug only
            self._show_configs(cfg, suffix=u'Wait to start BCI app...')
            time.sleep(5)
            self._shuffle_freqs(cfg)
            self._send_csp_info(cfg)
            ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
            self._run_next_scenario()
        elif self.mode == 'manual':
            self._show_configs(cfg, suffix=u'Suggested frequencies:')
            self._edit_configs(cfg)
            self._send_csp_info(cfg)
            ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
            self._run_next_scenario()
        elif self.mode == 'retry_on_failure':
            if self._determine_means(cfg):
                self._show_configs(cfg, suffix=u'Wait to start BCI app...')
                time.sleep(5)
                self._shuffle_freqs(cfg)
                self._send_csp_info(cfg)
                ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
                self._run_next_scenario()
            else:
                self._show_configs(cfg, suffix=u'Calibration FAILED, Try again with another freqs...')
                time.sleep(5)
                self._send_csp_info(cfg)
                self._run_prev_scenario()
        elif self.mode == 'abort_on_failure':
            if self._determine_means(cfg):            
                self._show_configs(cfg, suffix=u'Wait to start BCI app...')
                time.sleep(5)
                self._shuffle_freqs(cfg)
                self._send_csp_info(cfg)
                ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
                self._run_next_scenario()
            else:
                self._show_configs(cfg, suffix=u'Calibration FAILED, You are not working, Bye...')
                time.sleep(5)
                self._send_csp_info(cfg)
                #sys.exit(1)
        else:
            self.logger.warning("Unrecognised mode: "+self.mode)
                
    def _determine_means(self, cfg):
        """Return true if means are ok"""
        all_means = [float(i) for i in cfg['all_means'].split(';')]
        ret = all_means[cfg['dec_count']-1] >= cfg['value'][0]

        self.logger.info("Determine means, means: "+str(all_means)+" treshold: "+str(cfg['value'][0]))
        self.logger.info("Is smallest mean bigger than treshold?: "+str(ret))
        return ret

    def _shuffle_freqs(self, cfg):
   
        if self.config.get_param('shuffle_freqs') == '0':
            return

        elif self.config.get_param('shuffle_freqs') == '1':
             #Move second best freq to the last field...
            freqs = [int(i) for i in cfg['freqs'].split(';')]
            new_freqs = []
            new_freqs.append(freqs[0])
            for f in freqs[3:]:
                new_freqs.append(f)
            new_freqs.append(freqs[2])
            new_freqs.append(freqs[1])

        elif self.config.get_param('shuffle_freqs') == 'random':
            new_freq = [int(i) for i in cfg['freqs'].split(';')]
            random.shuffle(new_freqs)
        
        cfg['freqs'] = ';'.join([str(i) for i in new_freqs])
        
    def _show_configs(self, cfg, suffix=u""):
        text_id = int(self.config.get_param('ugm_text_id'))
        all_freqs = cfg['all_freqs'].split(';')
        all_means = cfg['all_means'].split(';')
        ugm_helper.send_config_for(
            self.conn, text_id, 'message',
            u''.join([u"Best frequencies:"# i ich sila:",
                     '\n',
                     #' '.join([all_freqs[i]+" ("+all_means[i]+")" for i in range(len(all_freqs))]),
                      ' '.join([all_freqs[i] for i in range(len(all_freqs))]),
                     #'\n',
                     #u'Suggested buffer length: '+str(cfg['buffer'])+" secs",
                     '\n',
                     suffix
                     ])
            )

    def _edit_configs(self, cfg):
        buffer = float(cfg['buffer'])
        freqs = [int(i) for i in cfg['freqs'].split(';')]
        self.logger.info("Configs before edit:")
        self.logger.info("Buffer: "+str(buffer)+" freqs: "+str(freqs))
        buffer, freqs = ssvep_csp_helper.edit_csp_configs(buffer, freqs)
        cfg['buffer'] = buffer
        cfg['freqs'] = ';'.join([str(i) for i in freqs])
        self.logger.info("Configs after edit:")
        self.logger.info("Buffer: "+str(buffer)+" freqs: "+str(freqs))

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


        
