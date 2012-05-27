#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os, time
import numpy as np

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer


from analysis.obci_signal_processing import read_manager
from analysis.obci_signal_processing.tags import smart_tag_definition as df
from analysis.obci_signal_processing import smart_tags_manager as sgr
from configs import settings
from acquisition import acquisition_helper
from gui.ugm import ugm_helper
#from interfaces.bci.ssvep_csp import logic_ssvep_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper

from logic import logic_helper
from logic import logic_logging as logger

import signalParser as sp
from p300_draw import P300_draw
from p300_fda import P300_train


LOGGER = logger.get_logger("p300_fda", 'info')

class LogicP300Fda(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicP300Fda, self).__init__(addresses=addresses,
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
        LOGGER.info("START FDA...")

        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        in_file = acquisition_helper.get_file_path(f_dir, f_name)

        filename = os.path.join(f_dir, f_name + ".obci")
        data = sp.signalParser(filename)
            
        fs = int(float(data.getSamplingFrequency()))

        mgr = read_manager.ReadManager(
            in_file+'.obci.xml',
            in_file+'.obci.raw',
            in_file+'.obci.tag')
        
        if self.use_channels is None:
            self.use_channels = data.getChannelList()
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
        
        ## Get data and tags
        data.setMontage(self.montage_channels)
        Signal = data.getData(self.use_channels)
        trgTags = data.get_p300_tags()
        ntrgTags = data.get_not_p300_tags()

        target, nontarget = data.getTargetNontarget(Signal, trgTags, ntrgTags)

        ## Get params from file
        pVal = float(self.config.get_param("p_val"))
        nRepeat = int(self.config.get_param("n_repeat"))
        nMin = int(self.config.get_param("n_min"))
        nMax = int(self.config.get_param("n_max"))
        
        avrM_l = map(lambda x: int(x), self.config.get_param("avr_m").split(';'))
        conN_l = map(lambda x: int(x), self.config.get_param("con_n").split(';'))
        csp_dt_l = map(lambda x: float(x), self.config.get_param("csp_dt").split(';'))
        csp_time_l = map(lambda x: float(x), self.config.get_param("csp_time").split(';'))

        ## Define buffer
        buffer = 1.1*fs
        LOGGER.info("Computer buffer len: "+str(buffer))

        
        ## Make montage matrix
        conf = self.use_channels, self.montage, self.montage_channels
        self.montage_matrix = self._get_montage_matrix(conf[0], conf[1], conf[2], mgr.get_param('channels_names'))
        print "self.montage_matrix: ", self.montage_matrix


        channels = ";".join(self.use_channels)
        
        # make sure that:
        # channels -- is in format like "P07;O1;Oz;O2"
        # fs -- is a number
        # avrM -- are int
        # conN -- are int
        # csp_time -- is a list of two float 0 < x < 1
        N = 0
        d = {}
        for avrM in avrM_l:
            for conN in conN_l:
                for csp_time in csp_time_l:
                    for dt in csp_dt_l:
                        d[N] = {"avrM":avrM, "conN":conN, "csp_time":[csp_time, csp_time+dt]}
                        print "d[%i] = " %N, d[N]
                        N += 1
        
        #################################
        ## CROSS CHECKING
        P_dict, dVal_dict = {}, {}
        l = np.zeros(N)
        for idxN in range(N):
            KEY = d[idxN].keys()
            for k in KEY:
                #~ c = "{0} = {1}".format(k, d[idxN][k])
                #~ print c
                #~ exec(c)
                exec "{0}_tmp = {1}".format(k, d[idxN][k]) in globals(), locals()
                
            p300 = P300_train(channels, fs, avrM_tmp, conN_tmp, csp_time_tmp)
            l[idxN] = p300.valid_kGroups(Signal, target, nontarget, 2)
            P_dict[idxN] = p300.getPWC()
            dVal_dict[idxN] = p300.getDValDistribution()
            p300.saveDist2File("target_%i"%idxN, "nontarget_%i"%idxN)

        #################################
        distributionDraw = P300_draw(fs)
        # Plot all d distributions
        for idx in range(N):
            dTarget, dNontarget = dVal_dict[idx]
            distributionDraw.plotDistribution(dTarget, dNontarget)


        #################################
        # Finding best    

        print "\n"*5
        print "L: ", l
        P, conN, avrM, csp_time = None, None, None, None
        BEST = -1
        arr = np.arange(len(l))
        for i in range(5):
            bestN = int(arr[l==l.max()])
            
            print "best_{0}: {1}".format(i, bestN)
            print "d[bestN]: ", d[bestN]
            print "l[bestN]: ", l.max()
            if (l.max() < 1000) and (BEST == -1): BEST = bestN
            l[bestN] = l.min()-1

        print "best: ", BEST

        P, w, c = P_dict[BEST]
        dTarget, dNontarget = dVal_dict[BEST]
        c = st.scoreatpercentile(dNontarget, pVal)
        
        avrM = d[BEST]["avrM"]
        conN = d[BEST]["conN"]
        csp_time = d[BEST]["csp_time"]

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
        
        f_name = self.config.get_param("csp_file_name")
        f_dir = self.config.get_param("csp_file_path")
        ssvep_csp_helper.set_csp_config(f_dir, f_name, cfg)

        ## Plotting best
        p300_draw = P300_draw()
        p300_draw.setCalibration(target, nontarget)
        p300_draw.setCSP(P)
        p300_draw.setTimeLine(conN, avrM, csp_time)
        p300_draw.plotSignal()
        p300_draw.plotSignal_ds()
        
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
    
    def _get_montage_matrix(self, use_channels, montage, montage_channels, channels_names):
        if type(use_channels) == type("Pz;Oz"):
            use_channels = use_channels.split(';')
        if type(montage_channels) == type("Pz;Oz"):
            montage_channels = montage_channels.split(';')
        return ssvep_csp_helper.get_montage_matrix(
            channels_names,
            use_channels,
            montage,
            montage_channels)

if __name__ == "__main__":
    LogicP300Csp(settings.MULTIPLEXER_ADDRESSES).loop()
