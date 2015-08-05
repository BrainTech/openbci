# -*- coding: utf-8 -*-
#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>
#
import os.path

import numpy as np

import pickle

from obci.analysis.obci_signal_processing import read_manager

import obci.analysis.mgr_ssvep.signal_processing.filters as SPF
import obci.analysis.mgr_ssvep.signal_processing.parse_signal as SPPS
import obci.analysis.mgr_ssvep.signal_processing.montage_signal as SPSM
import obci.analysis.mgr_ssvep.signal_processing.csp_analysis as SPCSP
import obci.analysis.mgr_ssvep.signal_processing.calibration_analysis as SPCA

from obci.analysis.mgr_ssvep.data_analysis.pattern2 import Patterns

import obci.analysis.mgr_ssvep.data_analysis.display as display


class ClassificationSsvepPattern(object):
    def __init__(self, config_file_dir, config_file_name, 
                 ignore_channels,
                 montage_type, 
                 montage_channels, 
                 leave_channels, 
                 all_channels,
                 channels_gains,
                 display_flag=False,
                 l_pattern=1,
                 sampling_frequency=512.0):

        super(ClassificationSsvepPattern, self).__init__()
        self.conf_file_name = config_file_name
        self.conf_file_dir = config_file_dir
        self._read_conf_file()
        self.fs = sampling_frequency
        self.l_pattern = l_pattern
        self.ignore_channels = ignore_channels
        self.leave_channels = leave_channels
        self.channels_gains = channels_gains
        self.all_channels = all_channels
        self.montage_channels = montage_channels
        self.use_channels = self._init_channels_names()

        self.display_flag = display_flag

    def _to_volts(self, signal, channels_gains):#
        return SPPS.to_volts(signal, channels_gains)

    def _init_channels_names(self):
        use_channels = []

        for ch_name in self.all_channels:
            if ch_name not in self.ignore_channels and \
               ch_name not in self.montage_channels:

                use_channels.append(ch_name)

        return use_channels

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

    def _read_conf_file(self):
        file_name = os.path.expanduser(os.path.join(self.conf_file_dir, self.conf_file_name))
        with open(file_name, 'rb') as handle:
            values = pickle.load(handle)

        self.freqs = values['freq']
        self.csp_montage = values['csp_montage']
        self.patterns = values['patterns']
        self.classyficator = values['classyficator']
        self.montage_matrix = values['montage_matrix']

    def _get_predictions(self, patterns, freqs):
        result = [float(np.corrcoef(self.patterns[f], patterns[ind])[0][1]) for ind, f in enumerate(freqs)]
        print result
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
        # self.all_channels = sum([[self.csp_channel_name], self.leave_channels], [])
        return signal

    def run(self, signal, freqs):
        signal = self._signal_processing(signal)
        self.signal_pattern_test = Patterns(signal, self.l_pattern, self.csp_channel_name, self.leave_channels, sum([[self.csp_channel_name], self.leave_channels], []), self.fs)
        patterns = self.signal_pattern_test.calculate()
        re, predictions = self._get_predictions(patterns, freqs)
        print predictions, sum(predictions)
        if sum(predictions) == 1:
            print "send freq[predictions.index(1)]", predictions.index(1)
        else:
            print "brak decyzji"
        return re
