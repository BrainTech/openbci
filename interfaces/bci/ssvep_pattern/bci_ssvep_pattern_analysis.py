#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time, pickle, os.path
import numpy as np
from scipy.signal import hamming
import scipy.stats as st
from obci.utils import context as ctx

import obci.analysis.mgr_ssvep.signal_processing.filters as SPF
import obci.analysis.mgr_ssvep.signal_processing.parse_signal as SPPS
import obci.analysis.mgr_ssvep.signal_processing.montage_signal as SPSM
import obci.analysis.mgr_ssvep.signal_processing.csp_analysis as SPCSP
import obci.analysis.mgr_ssvep.signal_processing.calibration_analysis as SPCA

from obci.analysis.mgr_ssvep.data_analysis.pattern2 import Patterns

import obci.analysis.mgr_ssvep.data_analysis.display as display

DEBUG = False

class BCISsvepPatternAnalysis(object):
    def __init__(self, send_func, freqs, cfg, channels_names, channels_gains, sampling, 
                 context=ctx.get_dummy_context('BCISsvepPatternAnalysis'), display_flag=False):
        self.logger = context['logger']
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        self.freqs_to_ = sum([freqs[4:], freqs[:4]], [])
        allFreqs = freqs

        self.indexMap = {}
        k = 0
        for i in range(len(allFreqs)):
            if allFreqs[i] != 0:
                self.indexMap[allFreqs[i]] = k
                k += 1
        self.freqs = self.indexMap.keys()

        self.logger.info("Have freqs:")
        self.logger.info(str(self.freqs))
        self.logger.info("indexMap:")
        self.logger.info(str(self.indexMap))

        self.csp_montage = cfg['csp_montage']
        self.patterns = cfg['patterns']
        self.classyficator = cfg['classyficator']
        self.csp_montage = cfg['csp_montage']
        self.patterns  = cfg['patterns']
        self.l_pattern = cfg['l_pattern']
        self.channels_gains = channels_gains
        self.all_channels = channels_names
        self.use_channels = cfg['use_channels'].split(';')

        self.leave_channels = cfg['leave_channels'].split(';')
        self.montage_matrix = cfg['montage_matrix']
        self.montage_channels = cfg['montage_channels'].split(';')

        self.display_flag = display_flag

    def _to_volts(self, signal, channels_gains):#
        return SPPS.to_volts(signal, channels_gains) 

    def _highpass_filtering(self, signal, use_channels, all_channels, fs):#
        return SPF.highpass_filter(signal, use_channels, all_channels, fs)

    def _bandpass_filtering(self, signal, use_channels, all_channels, fs):#
        return SPF.cheby2_bandpass_filter(signal, use_channels, all_channels, fs)

    def _montage_signal(self, signal, montage_matrix):#  
        return SPSM.montage(signal, montage_matrix)

    def _apply_csp_montage(self, signal, csp_montage,  csp_channel, all_channels, leave_channels):
        return SPCSP.apply_csp_montage(signal, csp_montage,  csp_channel, all_channels, leave_channels)

    def _display_signal(self, signal, channels_to_display, all_channels, title = ''):
        display.display_signal(signal, channels_to_display, all_channels, title)

    def _display_patterns(self, patterns):
        data_to_display = np.zeros((len(patterns.keys()),
                                    len(patterns.values()[0].pattern)))
        labels = []

        for ind, freq in enumerate(patterns.keys()):
            labels.append(freq)
            data_to_display[ind] = patterns[freq].pattern

        display.display_patterns(labels, data_to_display)

    def _display_patterns_test(self, patterns):
        data_to_display = np.zeros((len(patterns.keys()),
                                    len(patterns.values()[0].pattern[0])))
        labels = []

        for ind, freq in enumerate(patterns.keys()):
            labels.append(freq)
            data_to_display[ind] = patterns[freq].pattern[4]

        display.display_patterns(labels, data_to_display)

    def _get_predictions(self, patterns, freqs):
        result = [float(np.corrcoef(self.patterns[str(f)], patterns[ind])[0][1]) for ind, f in enumerate(freqs)]
        return result, [float(self.classyficator.predict([value])) for value in result]
   

    def _signal_processing(self, signal):
        #0. to volts
        signal = self._to_volts(signal, self.channels_gains)
        if self.display_flag:
            self._display_signal(signal, self.use_channels, self.all_channels, 'test_to_voltage') 

        #1. cutof mean signal
        signal = self._highpass_filtering(signal, 
                                          sum([self.use_channels, 
                                               self.montage_channels], []),
                                          self.all_channels,
                                          self.fs)
        if self.display_flag:
            self._display_signal(signal, 
                                 sum([self.use_channels, self.montage_channels], []), 
                                 self.all_channels,
                                 'test_highpass')
        
        #2. bandpass filtering (ss.cheby2(3, 50,[49/(fs/2),50/(fs/2)], btype='bandstop', 
        #                    analog=0))

        signal = self._bandpass_filtering(signal, 
                                          sum([self.use_channels, 
                                               self.montage_channels], []),
                                          self.all_channels,
                                          self.fs)
        if self.display_flag:
            self._display_signal(signal, 
                                 sum([self.use_channels, self.montage_channels], []), 
                                 self.all_channels,
                                 'test_bandpass')

        #3. montage signal
        signal = self._montage_signal(signal, 
                                      self.montage_matrix)
        all_channels = sum([self.use_channels, self.leave_channels], [])
        if self.display_flag:
            self._display_signal(signal, 
                                 self.use_channels, 
                                 all_channels, 
                                 'test_montage')
        print "***********************************************************"
        print self.use_channels, self.csp_montage, all_channels, self.leave_channels
        #4. apply csp montage
        signal, self.csp_channel_name = self._apply_csp_montage(signal, 
                                                                self.csp_montage, 
                                                                self.use_channels,
                                                                all_channels, 
                                                                self.leave_channels)
        if self.display_flag:
             self._display_signal(signal, 
                                  [self.csp_channel_name], 
                                  sum([[self.csp_channel_name], self.leave_channels], []), 
                                  'csp')
        return signal

    def analyse(self, data):
        print '############################################################'
        print data.shape
        self.logger.debug("Got data to analyse... after: "+str(time.time()-self.last_time))
        self.logger.debug("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        self.last_time = time.time()
        signal = self._signal_processing(data)
        self.signal_pattern_test = Patterns(signal, self.l_pattern, self.csp_channel_name, self.leave_channels, sum([[self.csp_channel_name], self.leave_channels], []), self.fs)
        patterns = self.signal_pattern_test.calculate()
        print '***********************************************'
        print self.freqs
        re, predictions = self._get_predictions(patterns, self.freqs_to_)
        self.logger.info("cor.:{}, predictions:{}".format(str(re), str(predictions)))
        if DEBUG:
            if random.random() > 0.5:
                freq = random.choice(self.indexMap.keys())
        if sum(predictions) == 1:
            f = self.freqs[predictions.index(1)]
            self.send_func(self.indexMap[f])
        else:
            self.logger.info("Got  - no decision")


                    
