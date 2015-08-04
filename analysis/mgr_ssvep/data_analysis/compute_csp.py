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

from obci.analysis.obci_signal_processing import read_manager

import obci.analysis.mgr_ssvep.signal_processing.filters as SPF
import obci.analysis.mgr_ssvep.signal_processing.parse_signal as SPPS
import obci.analysis.mgr_ssvep.signal_processing.montage_signal as SPSM
import obci.analysis.mgr_ssvep.signal_processing.csp_analysis as SPCSP

class ComputeCSP(object):
    def __init__(self, file_dir, file_name, l_trial, use_channels,
                 montage_type, montage_channels, tag_name,
                 freqs):

        super(ComputeCSP, self).__init__()
        self.file_name = file_name
        self.file_dir = file_dir
        self.mgr = self._init_read_manager()

        self.channels_gains = self.mgr.get_param('channels_gains')
        self.all_channels = self.mgr.get_param('channels_names')
        self.fs = float(self.mgr.get_param("sampling_frequency"))
        self.l_trial = l_trial
        self.montage_type = montage_type
        self.montage_channels = montage_channels
        self.tag_name = tag_name
        self.use_channels = use_channels
        self.freq_to_train = freqs
        self.montage_matrix = self._init_montage_matrix(self.all_channels, 
                                                        self.use_channels, 
                                                        self.montage_type, 
                                                        self.montage_channels)

    def _get_file_name(self, file_dir, file_name):#
        return os.path.expanduser(os.path.join(file_dir, file_name))

    def _init_read_manager(self):#
        file_name = self._get_file_name(self.file_dir, self.file_name)
        return read_manager.ReadManager(file_name+'.obci.xml', 
                                        file_name+'.obci.raw', 
                                        file_name+'.obci.tag')

    def _init_montage_matrix(self, all_channels, use_channels, montage_type, 
                             montage_channels):
        return SPSM.get_montage_matrix(all_channels, use_channels, montage_type, 
                                       montage_channels)

    def _to_volts(self, signal, channels_gains):#
        return SPPS.to_volts(signal, channels_gains)
        
    def _highpass_filtering(self, signal, use_channels, all_channels, fs):#
        return SPF.highpass_filter(signal, use_channels, all_channels, fs)

    def _bandpass_filtering(self, signal, use_channels, all_channels, fs):#
        return SPF.cheby2_bandpass_filter(signal, use_channels, all_channels, fs)

    def _montage_signal(self, signal, montage_matrix):#
        self.all_channels = self.use_channels
        return SPSM.montage(signal, montage_matrix)

    def _signal_segmentation(self, mgr, l_trial, tag_name):
        return SPPS.signal_segmentation(mgr, l_trial, 0, tag_name)

    def _csp_calculate(self, smart_tags, use_channels, freq_to_train, fs):
        return SPCSP.csp_compute(smart_tags, use_channels, freq_to_train, fs)

    
    def calculate(self):
        signal = self.mgr.get_samples()
        #1. to voltage
        signal = self._to_volts(signal, self.channels_gains)

        #2. cutoff mean sig
        signal = self._highpass_filtering(signal, 
                                          sum([self.use_channels, 
                                               self.montage_channels], []),
                                          self.all_channels,
                                          self.fs)

        #3. bandpass filtering (ss.cheby2(3, 50,[49/(fs/2),50/(fs/2)], btype='bandstop', 
        #                       analog=0))
        signal = self._bandpass_filtering(signal, 
                                          sum([self.use_channels, 
                                               self.montage_channels], []),
                                          self.all_channels,
                                          self.fs)


        #4. apply montage
        signal = self._montage_signal(signal,
                                      self.montage_matrix) 


        self.mgr.set_samples(signal, self.use_channels)
        
        #5. signal segmentation
        self.smart_tags = self._signal_segmentation(self.mgr, 
                                                    self.l_trial, 
                                                    self.tag_name)
        
        #6. calculate csp
        self.P, self.vals = self._csp_calculate(self.smart_tags, 
                                                self.use_channels, 
                                                self.freq_to_train,
                                                self.fs)

