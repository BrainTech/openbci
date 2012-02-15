#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os, time
import numpy as np

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from analysis.obci_signal_processing import read_manager
from configs import settings
from acquisition import acquisition_helper
from gui.ugm import ugm_helper
#from interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper
import p300
from logic import logic_helper

from logic import logic_logging as logger
LOGGER = logger.get_logger("p300_csp", 'info')

class LogicP300Csp(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicP300Csp, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CSP)
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
        LOGGER.info("START CSP...")
        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        in_file = acquisition_helper.get_file_path(f_dir, f_name)
	mgr = read_manager.ReadManager(
		in_file+'.obci.xml',
		in_file+'.obci.raw',
		in_file+'.obci.tag')
        fs = int(float(mgr.get_param("sampling_frequency")))
	if self.use_channels is None:
		self.use_channels = mgr.get_param('channels_names')
	if self.ignore_channels is not None:
		for i in self.ignore_channels:
			try:
				self.use_channels.remove(i)
			except:
				pass

        LOGGER.info("USE CHANNELS: "+str(self.use_channels))
        data = p300.p300_train(
            in_file+'.obci',
            self.use_channels, fs, self.montage_channels, self.montage, idx=1)#idx oznacza indeks na który
        new_tags = data.wyr()
        not_idx_tags = data.data.get_p300_tags(idx=-1, samples=False)#Tutaj idx musi być -idx z linijki 11
                                                            #Tagi pozostałych przypadków
        mean, left, right = data.get_mean(new_tags, m_time=[0, 0.5])
        buffer = 0.5
        mean[:left] = 0
        mean[right:] = 0
        sr = 5 #Maksymalna liczba odcinków do uśrednienia; gdzieś do parametryzacji
        targets = np.zeros([sr, len(new_tags)])
        non_targets = np.zeros([sr, len(not_idx_tags)])
        mu = np.zeros(sr)
        sigma = np.zeros(sr)
        for i in xrange(1, sr + 1):
            x = data.get_n_mean(i, new_tags, [0.1, 0.5], 0.05)
            targets[i - 1, :], non_targets[i - 1, :], mu[i - 1], sigma[i - 1] = x            
        q = data
        cfg = {
             'mu': mu,
             'sigma': sigma,
             'mean':mean,
             'targets':targets,
             'non_targets':non_targets,
             'q' : q,
             'buffer':buffer,
	     'use_channels':';'.join(self.use_channels),
	     'montage':self.montage,
	     'montage_channels':';'.join(self.montage_channels)
             }

        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)
        LOGGER.info("CSP DONE")
        if not self.run_offline:
            self._run_next_scenario()

    def _run_next_scenario(self):
        path = self.config.get_param('next_scenario_path')
        if len(path) > 0:
            logic_helper.restart_scenario(path)
        else:
            LOGGER.info("NO NEXT SCENARIO!!! Finish!!!")
            sys.exit(0)

if __name__ == "__main__":
    LogicP300Csp(settings.MULTIPLEXER_ADDRESSES).loop()


        
