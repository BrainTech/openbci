#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os, time
import numpy as np

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

import signalParser as sp
from analysis.obci_signal_processing import read_manager
from configs import settings
from acquisition import acquisition_helper
from gui.ugm import ugm_helper
#from interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper
from interfaces.bci.p300_fda.p300_fda import P300_train
from logic import logic_helper
from logic import logic_logging as logger
from rysuj_p300 import P300_draw

LOGGER = logger.get_logger("p300_fda", 'info')

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

        self.montage = self.config.get_param("montage")
        tmp = self.config.get_param("montage_channels")
        if len(tmp) > 0:
            self.montage_channels = tmp.split(';')
        else:
            self.montage_channels = []


        LOGGER.info("USE CHANNELS: "+str(self.use_channels))
        LOGGER.info("CHANNELS NAMES: "+str(mgr.get_param('channels_names')))


        fn = in_file+'.obci'
        raw = mgr.get_channels_samples(self.use_channels)#sp.signalParser(fn)
        trgTags = [x['start_timestamp'] for x in mgr.get_tags('blink', p_func=lambda t: t['desc']['index'] == '1')]
        ntrgTags = [x['start_timestamp'] for x in mgr.get_tags('blink', p_func=lambda t: t['desc']['index'] != '1')]

        trgTags = np.array(trgTags)*fs
        ntrgTags = np.array(ntrgTags)*fs
        
        #self.data = None
        #self.data.setMontage(self.montage_channels, self.montage)
        
        #~ trgTags = self.data.get_p300_tags()
        #~ ntrgTags = self.data.get_not_p300_tags()        
        #~ signal = self.data.extract_channel(self.use_channels)

        csp_time = [0.25,0.75]
        pVal = 0.8
        nRepeat = 3
        avrM = 2
        conN = 2
        P = None
        w = None
        c = None

        buffer = 1.1*fs
        LOGGER.info("Computer buffer len: "+str(buffer))

        
        cfg = {"csp_time":csp_time,
                "use_channels": ';'.join(self.use_channels),
                'pVal':pVal,
                'avrM':avrM,
                'conN':conN,
                "nRepeat":nRepeat,
                "P":P,
                "w":w,
                "c":c,
                "montage":self.montage,
                "montage_channels":';'.join(self.montage_channels),
                "buffer":buffer
                }

        self.montage_matrix = self._get_montage_matrix(cfg, mgr.get_param('channels_names'))
        signal = np.dot(self.montage_matrix, raw)

        channels = ";".join(self.use_channels)
        
        # make sure that:
        # channels -- is in format like "P07;O1;Oz;O2"
        # fs -- is a number
        # avrM -- is a int
        # conN -- is a int
        # csp_time -- is a list of two float 0 < x < 1
        p300 = P300_train(channels, fs, avrM, conN, csp_time)
        p300.trainClassifier(signal, trgTags, ntrgTags)
        P, w, c = p300.getPWC()
        
        cfg['P'] = P
        cfg['w'] = w
        cfg['c'] = c

        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)

        target, nontarget = p300.getTargetNontarget(signal, trgTags, ntrgTags)
        p300_draw = P300_draw(target, nontarget, trgTags, ntrgTags)
        p300_draw.setCSP(P=P)
        p300_draw.setTimeLine(conN, avrM, csp_time)
        p300_draw.plot()
        
        LOGGER.info("CSP DONE")
        if not self.run_offline:
            self._run_next_scenario()

    def _run_next_scenario(self):
        path = self.config.get_param('next_scenario_path')
        if len(path) > 0:
            logic_helper.restart_scenario(self.conn, path, leave_on=['amplifier'])
        else:
            LOGGER.info("NO NEXT SCENARIO!!! Finish!!!")
            sys.exit(0)
    
    def _get_montage_matrix(self, cfg, channels_names):
        return ssvep_csp_helper.get_montage_matrix(
            channels_names,
            cfg['use_channels'].split(';'),
            cfg['montage'],
            cfg['montage_channels'].split(';'))

if __name__ == "__main__":
    LogicP300Csp(settings.MULTIPLEXER_ADDRESSES).loop()
