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
import display 
import sys 
import ast
import obci.analysis.mgr_ssvep.signal_processing.pattern_analysis as SPPA
import numpy as np

class Patterns(object):
    """docstring for Pattern"""
    def __init__(self, signal, l_pattern, channel, diodas_channels, all_channels, fs, display_flag=False):

        super(Patterns, self).__init__()
        self.signal = signal
        self.all_channels=all_channels
        self.display_flag = display_flag
        self.fs = fs
        self.diodas_channels = diodas_channels
        self.channel = channel
        self.l_pattern = l_pattern

    def set_freq(self, freq):
        self.freq = freq

    def get_freq(self):
    	return self.freq

    def _display_signal(self, signal, channels_to_display, all_channels, title = ''):
        display.display_signal(signal, channels_to_display, all_channels, title)


    def _calculate_pattern_buffer(self, signal, diodas_channels, channel, all_channels, l_pattern, fs):
        l_pattern_samples = int(l_pattern*fs)
        patterns = []
        # import matplotlib.pyplot as plt
        # a=1
        # f = plt.figure()
        # for i in signal:
        #     ax = f.add_subplot(12,1,a)
        #     ax.plot(i)
        #     a+=1
        for ind, ch_name in enumerate(all_channels):
            if ch_name == channel:
                temp = signal[ind]


        for ind, ch_name in enumerate(all_channels):
            if ch_name in diodas_channels:
                s = np.array([])
                dioda_signal = np.array([])
                d_sig = signal[ind]
                p_sig = temp.copy()
                stimulus_starts_ind = np.where(d_sig >= 1)[0]
                s = np.concatenate((s, p_sig[int(stimulus_starts_ind[0]):int(stimulus_starts_ind[-1])]), axis=0)
                dioda_signal = np.concatenate((dioda_signal, d_sig[stimulus_starts_ind[0]:stimulus_starts_ind[-1]]), axis=0)
                blinks = np.where(dioda_signal == 1)[0]
                preper_signal = np.r_[s, s]
                patterns.append(np.mean(np.array([preper_signal[i:i+l_pattern_samples] for i in blinks]), axis=0))
        return patterns

    def _normalize_signal(self, signal, diodes_channels, all_channels):
        for ch_name, ch_sig in zip(all_channels, signal):
            if ch_name in diodes_channels:
                min_signal = ch_sig.min()
                ch_sig[:] -= np.ones(ch_sig.shape)*min_signal
                max_signal = ch_sig.max()
                ch_sig[:] /= max_signal

        return signal

    def _found_blinks(self, signal, diodes_channels, all_channels):
        for ch_name, ch_sig in zip(all_channels, signal):
            if ch_name in diodes_channels:
                flag, ind = 0, 0
                blinks = np.zeros(len(ch_sig))
                while ind < len(ch_sig):
                    if ch_sig[ind]<0.2:
                        if  flag == 0:
                            flag = 1
                    if (ch_sig[ind] > 0.8):
                        if flag==1:
                            flag = 0
                            blinks[ind] = 1
                    ind+=1
                ch_sig[:] = blinks    
        return signal

    def calculate(self):
            
        #1. normalize diodes signal
        self.signal = self._normalize_signal(self.signal, self.diodas_channels, self.all_channels)
        if self.display_flag:
            self._display_signal(self.signal, 
                                 self.diodas_channels, self.all_channels,
                                  'signal_part_0 diode normalize')
        #3. found blinks found 
        self.signal = self._found_blinks(self.signal, self.diodas_channels, self.all_channels)
        if self.display_flag:
            self._display_signal(self.signal, 
                                 self.diodas_channels, self.all_channels,
                                  'signal_part_0 found_blinks')   

        self.pattern = self._calculate_pattern_buffer(self.signal, self.diodas_channels, self.channel, self.all_channels, self.l_pattern, self.fs) 
        
        # a=1
        # import matplotlib.pyplot as plt
        # f = plt.figure()
        # for i in self.pattern:
        #     ax = f.add_subplot(8,1,a)
        #     ax.plot(i)
        #     a+=1

        # plt.show()
        return self.pattern



    	
        

