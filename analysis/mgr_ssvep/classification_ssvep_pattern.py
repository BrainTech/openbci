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

from obci.analysis.mgr_ssvep.data_analysis.compute_pattern2 import ComputePattern

import obci.analysis.mgr_ssvep.data_analysis.display as display


class ClassificationSsvepPattern(object):
    def __init__(self, config_file_dir, config_file_name, 
                 ignore_channels,
                 montage_type, 
                 montage_channels, 
                 leave_channels, 
                 all_channels,
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
        self.tag_name = tag_name
        self.use_channels = self._init_channels_names()
        self.leave_channels = leave_channels
        self.display_flag = display_flag

    # def _init_read_manager(self):
    #     file_name = os.path.expanduser(os.path.join(self.file_dir, self.file_name))

    #     return read_manager.ReadManager(file_name+'.obci.xml', 
    #                                     file_name+'.obci.raw', 
#     #                                     file_name+'.obci.tag')
#     def _to_volts(self, mgr):
#         return SPPS.to_volts(mgr)
    
#     def _init_channels_names(self):
#         all_channels = self.mgr.get_param('channels_names')
#         use_channels = []

#         for ch_name in all_channels:
#             if ch_name not in self.ignore_channels and \
#                ch_name not in self.montage_channels:

#                 use_channels.append(ch_name)

#         return use_channels

#     def _highpass_filtering(self, mgr, use_channels, fs):
#         return SPF.butter_highpass_filter(mgr, use_channels, fs)

#     def _bandpass_filtering(self, mgr, use_channels, fs):
#         return SPF.cheby2_bandpass_filter(mgr, use_channels, fs)

#     def _montage_signal(self, mgr, use_channels, 
#                         montage_type, montage_channels, 
#                         leave_channels):

#         return SPSM.montage(mgr, use_channels, montage_type, 
#                           montage_channels, leave_channels)

#     def _apply_csp_montage(self, mgr, csp_montage,  csp_channel, leave_channels):
#         return SPCSP.apply_csp_montage(mgr, csp_montage,  csp_channel, leave_channels)

#     def _display_signal(self, mgr, channels_to_display, title = ''):
#         display.display_signal(mgr, channels_to_display, title)

#     def _display_patterns_test(self, patterns):
#         data_to_display = np.zeros((len(patterns.keys()),
#                                     len(patterns.values()[0][0].pattern[0])))
#         labels = []

#         for ind, freq in enumerate(patterns.keys()):
#             labels.append(freq)
#             data_to_display[ind] = patterns[freq][0].pattern[5]

#         display.display_patterns(labels, data_to_display)

#     def read_conf_file()(self):
#         file_name = os.path.expanduser(os.path.join(self.conf_file_dir, self.conf_file_name))
#         with open(file_name, 'rb') as handle:
#             values = pickle.load(handle)
#         # self.fureq_to_train = values['freq']
#         self.csp_montage = values['csp_montage']
#         self.patterns = values['patterns']
#         self.nontarget_params = values['nontarget_params']
#         self.nontarget = values['nontarget']
#         self.target_old = values['target']
#         import matplotlib.pyplot as plt 
#         plt.figure()
#         self.nontarget_roz = []
#         self.target_roz = []
#         for i in self.nontarget.keys():
#             self.nontarget_roz.append(self.nontarget[i])
#             self.target_roz.append(self.target_old[i])
#             print i
#             plt.hist(self.nontarget[i])
#             plt.show()
#         print self.nontarget_roz
#         self.nontarget_roz = sum(self.nontarget_roz, [])
#         self.target_roz = sum(self.target_roz, [])
#         print self.nontarget_roz
#         a,b,c = plt.hist(self.nontarget_roz, range=(-1,1), bins=10)
#         self.nontarget_roz_2 = np.sort(self.nontarget_roz)

#         from sklearn.naive_bayes import GaussianNB
#         gnb = GaussianNB()
#         wszystkie = np.array(sum([self.nontarget_roz, self.target_roz], []))
#         l = np.array(sum([[0]*len(self.nontarget_roz), [1]*len(self.target_roz)], []))
#         print wszystkie.shape
#         targety = np.array(self.target_roz)
#         print targety.shape
#         gnb.fit(wszystkie.reshape(len(l), 1), l)
#         self.gnb = gnb

#     def _signal_segmentation(self, mgr, l_trial, offset, tag_name):
#         return SPPS.signal_segmentation(mgr, l_trial, offset, tag_name)


#     def run_test(self, calculate_pattern, calculate_pattern2, pattern):
#         results = {} 
#         results_2 = {} 
#         results_ = {}
#         gauss_1 = {}
#         gauss_2 = {}
#         targety = []
#         nontargety = []
#         w=[]
#         for key in calculate_pattern.keys():
#             results[key] = []
#             results_2[key] = []
#             results_[key] = []
#             gauss_1[key] = []
#             gauss_2[key] = []
#             for p, p1 in zip(calculate_pattern[key], calculate_pattern2[key]):
#                 a1 = [(float(np.corrcoef(pattern[key], pattern_test)[0][1])) for pattern_test in p.pattern]
#                 a1_ = [f for f in p.freqs]
#                 a2 = [(float(np.corrcoef(pattern[key], pattern_test)[0][1])) for pattern_test in p1.pattern]
#                 a2_ = [f for f in p1.freqs]


#                 targety.append([a for i,a in enumerate(a1) if i==5])
#                 targety.append([a for i,a in enumerate(a2) if i==5])
#                 nontargety.append([a for i,a in enumerate(a1) if i!=5])
#                 nontargety.append([a for i,a in enumerate(a2) if i!=5])

#                 results[key].append(a1)
#                 results[key].append(a2)
#                 results_[key].append(a1_)
#                 results_[key].append(a2_)
#                 results_2[key].append([(a-self.nontarget_params[key][0])/self.nontarget_params[key][1] for a in a1] )
#                 results_2[key].append([(a-self.nontarget_params[key][0])/self.nontarget_params[key][1]  for a in a2])
#                 # targety.append([a for i,a in enumerate(a1) if i==5])
#                 # targety.append([a for i,a in enumerate(a2) if i==5])
#                 # nontargety.append([a for i,a in enumerate(a1) if i!=5])
#                 # nontargety.append([a for i,a in enumerate(a2) if i!=5])

#                 gauss_1[key].append([self.gnb.predict([a]) for a in a1])
#                 w.append(gauss_1[key][-1])
#                 print gauss_1[key][-1], sum(gauss_1[key][-1])
#                 gauss_1[key].append([self.gnb.predict([a]) for a in a2]) 
#                 w.append(gauss_1[key][-1])

#                 # gauss_2[key].append([len(self.nontarget_roz_2[self.nontarget_roz_2.searchsorted(a):])/float(len(self.nontarget_roz_2)) for a in a1])
#                 # gauss_2[key].append([len(self.nontarget_roz_2[self.nontarget_roz_2.searchsorted(a):])/float(len(self.nontarget_roz_2)) for a in a2])
        

#         if self.display_flag==False:
#             import matplotlib.pyplot as plt
#             # plt.hist(w)
#             # plt.show()
#             plt.figure()
#             plt.hist(sum(nontargety, []))
#             plt.hist(self.nontarget_roz_2)

#             # plt.hist(sum(targety, []))
#             plt.figure()
#             plt.hist(sum(targety, []))
#             plt.hist(self.target_roz)

#             plt.show()
#             # display.display_results(results, self.auc_values)
#             # display.display_results(results_2, self.auc_values)
#             print sum([1 for i in w if (sum(i)[0]==1 and i[5] ==1)]), len(w)
#             print sum([1 for i in w if sum(i)[0]>1]), len(w)
#             print sum([1 for i in w if sum(i)[0]==0]), len(w)

#             display.display_results(gauss_1, self.auc_values)
#             # # print gauss1
#             # display.display_results(gauss_2, self.auc_values)
#         with open('test_1.pickle', 'wb') as handle:
#             pickle.dump(results, handle)

#         with open('test_2.pickle', 'wb') as handle:
#             pickle.dump(results_, handle)


#     def run(self):
#         self.read_conf_file()
#         #1. to voltage
#         self.mgr = self._to_volts(self.mgr)
#         #1. segmentation data
#         smart_tags1 = self._signal_segmentation(self.mgr, self.l_trial-self.l_train, 
#                                                     self.l_buffer_trenning, self.tag_name)
#         smart_tags2 = self._signal_segmentation(self.mgr, self.l_trial-self.l_train, 
#                                                     0, self.tag_name)
#         if self.display_flag:
#             self._display_signal(self.mgr, self.use_channels, 'test_to_voltage') 

#         for i in range(len(smart_tags1)):
#             #2. apply montage

#             smart_tags1[i] = self._montage_signal(smart_tags1[i], 
#                                             self.use_channels, 
#                                             self.montage_type, 
#                                             self.montage_channels, 
#                                             self.leave_channels)
            
#             smart_tags2[i] = self._montage_signal(smart_tags2[i], 
#                                             self.use_channels, 
#                                             self.montage_type, 
#                                             self.montage_channels, 
#                                             self.leave_channels)
#             if self.display_flag:
#                 self._display_signal(smart_tags1[i], self.use_channels, 'test_montage')


#             #3. highpass filtering cutoff mean sig

#             smart_tags1[i] = self._highpass_filtering(smart_tags1[i], 
#                                                 sum([self.use_channels, 
#                                                      self.montage_channels], []),
#                                                 self.fs)
#             smart_tags2[i] = self._highpass_filtering(smart_tags2[i], 
#                                                 sum([self.use_channels, 
#                                                      self.montage_channels], []),
#                                                 self.fs)
#             if self.display_flag:
#                 self._display_signal(smart_tags1[i], 
#                                      sum([self.use_channels, self.montage_channels], []), 
#                                      'test_highpass')
            
#             #4. bandpass filtering (ss.cheby2(3, 50,[49/(fs/2),50/(fs/2)], btype='bandstop', 
#             #                       analog=0))
#             smart_tags1[i] =self._bandpass_filtering(smart_tags1[i], 
#                                                 sum([self.use_channels, 
#                                                      self.montage_channels], []),
#                                                 self.fs)
#             smart_tags2[i] = self._bandpass_filtering(smart_tags2[i], 
#                                                 sum([self.use_channels, 
#                                                      self.montage_channels], []),
#                                                 self.fs)

#             if self.display_flag:
#                 self._display_signal(smart_tags1[i],  
#                                      sum([self.use_channels, self.montage_channels], []), 
#                                      'test_bandpass')
            
#             #5. apply csp montage
#             self.csp_channel_name = 'csp'
#             self.csp_channel_name, smart_tags1[i] = self._apply_csp_montage(smart_tags1[i], 
#                                                                       self.csp_montage, 
#                                                                       self.use_channels, 
#                                                                       self.leave_channels)
#             self.csp_channel_name, smart_tags2[i] = self._apply_csp_montage(smart_tags2[i], 
#                                                                       self.csp_montage, 
#                                                                       self.use_channels, 
#                                                                       self.leave_channels)

#             if self.display_flag:
#                  self._display_signal(smart_tags1[i].mgr, self.mgr.get_param("channels_names"), 'csp')

#         # 6. train test patterns
#         self.signal_pattern_test = ComputePattern(self.mgr, 
#                                                   self.freq_to_train,
#                                                   self.l_pattern, 
#                                                   self.l_trial-self.l_train,
#                                                   self.l_train,
#                                                   self.l_buffer_trenning,
#                                                   self.tag_name,
#                                                   self.csp_channel_name,
#                                                   self.leave_channels,
#                                                   self.active_field,
#                                                   type_pattern='buffer',
#                                                   all_field=True)

#         self.patterns_test = self.signal_pattern_test.calculate(smart_tags1)
#         if self.display_flag:
#             self._display_patterns_test(self.patterns_test)

#         self.signal_pattern_test2 = ComputePattern(self.mgr, 
#                                                   self.freq_to_train,
#                                                   self.l_pattern, 
#                                                   self.l_trial-self.l_train,
#                                                   self.l_train,
#                                                   0,
#                                                   self.tag_name,
#                                                   self.csp_channel_name,
#                                                   self.leave_channels,
#                                                   self.active_field,
#                                                   type_pattern='buffer',
#                                                   all_field=True)

#         self.patterns_test2 = self.signal_pattern_test2.calculate(smart_tags2)
#         if self.display_flag:
#             self._display_patterns_test(self.patterns_test2)

#         self.run_test(self.patterns_test, self.patterns_test2, self.patterns)

if __name__ == '__main__':
    test = TestClassification('dane_mgr_ania_1', '~/syg', '~/', 'conf_ssvep.pickle')
    test.run()