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
import ast

import numpy as np

import pickle

from obci.analysis.obci_signal_processing import read_manager
import matplotlib.pyplot as plt 
import obci.analysis.mgr_ssvep.signal_processing.filters as SPF
import obci.analysis.mgr_ssvep.signal_processing.parse_signal as SPPS
import obci.analysis.mgr_ssvep.signal_processing.montage_signal as SPSM
import obci.analysis.mgr_ssvep.signal_processing.csp_analysis as SPCSP
import obci.analysis.mgr_ssvep.signal_processing.calibration_analysis as SPCA

import obci.analysis.mgr_ssvep.data_analysis.display as display
from obci.analysis.mgr_ssvep.data_analysis.compute_csp import ComputeCSP
from obci.analysis.mgr_ssvep.data_analysis.pattern2 import Patterns

import operator

from sklearn.naive_bayes import GaussianNB

CHANNELS_TO_IGNORE = [u'Dioda1',u'Dioda2',u'Dioda3',u'Dioda4',
                  u'Dioda5',u'Dioda6',u'Dioda7',u'Dioda8',
                  u'AmpSaw', u'DriverSaw']

CHANNELS_TO_MONTAGE = [u'PO7']

CHANNELS_TO_LEAVE = [u'Dioda1',u'Dioda2',u'Dioda3',u'Dioda4',
                     u'Dioda5',u'Dioda6',u'Dioda7',u'Dioda8']

MONTAGE_TYPE = 'diff'

FREQ_TO_TRAIN = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]

class ComputeCalibration(object):
    def __init__(self, file_name, file_dir,                  
                 output_file_dir,
                 output_file_name,
                 l_trial=5, 
                 ignore_channels=CHANNELS_TO_IGNORE,
                 montage_type=MONTAGE_TYPE, 
                 montage_channels=CHANNELS_TO_MONTAGE, 
                 leave_channels=CHANNELS_TO_LEAVE, 
                 tag_name=u'diodes', 
                 freq_to_train=FREQ_TO_TRAIN, 
                 active_field=1,
                 display_flag=False,
                 l_pattern=1,
                 l_train=2,
                 l_buffer_trenning=2):

        super(ComputeCalibration, self).__init__()
        self.file_dir = file_dir
        self.file_name = file_name
        self.output_file_dir = output_file_dir
        self.output_file_name = output_file_name
        self.mgr = self._init_read_manager()
        self.channels_gains = self.mgr.get_param('channels_gains')
        self.all_channels = self.mgr.get_param('channels_names')
        self.fs = float(self.mgr.get_param("sampling_frequency"))
        self.l_trial = l_trial
        self.l_pattern = l_pattern
        self.l_train = l_train
        self.l_buffer_trenning=l_buffer_trenning
        self.ignore_channels = ignore_channels
        self.montage_type = montage_type
        self.montage_channels = montage_channels
        self.tag_name = tag_name
        self.freq_to_train = freq_to_train
        self.active_field = active_field
        self.use_channels = self._init_channels_names()
        self.leave_channels = leave_channels
        self.display_flag = display_flag
        self.montage_matrix = self._init_montage_matrix(self.all_channels, 
                                                        self.use_channels, 
                                                        self.montage_type, 
                                                        self.montage_channels, 
                                                        self.leave_channels)
        self.freqs_number = 8

    def _get_file_name(self, file_dir, file_name):#
        return os.path.expanduser(os.path.join(file_dir, file_name))

    def _init_read_manager(self):#
        file_name = self._get_file_name(self.file_dir, self.file_name)
        return read_manager.ReadManager(file_name+'.obci.xml', 
                                        file_name+'.obci.raw', 
                                        file_name+'.obci.tag')
    def _init_montage_matrix(self, all_channels, use_channels, montage_type, 
                             montage_channels, leave_channels):
        return SPSM.get_montage_matrix(all_channels, use_channels, montage_type, 
                                       montage_channels, leave_channels)

    def _to_volts(self, signal, channels_gains):#
        return SPPS.to_volts(signal, channels_gains)
    
    def _init_channels_names(self):
        use_channels = []

        for ch_name in self.mgr.get_param('channels_names'):
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

    def _signal_segmentation(self, mgr, l_trial, offset, tag_name):
        return SPPS.signal_segmentation(mgr, l_trial, offset, tag_name)



    def calibration_trainer(self, patterns_trenning, patterns_test_target, patterns_test_nontarget):
        # patterns_target_test, patterns_nontarget_test = {}, {}
        # for key in patterns_test.keys():
        #     if 'non' in key:
        #         patterns_nontarget_test[key.split('_')[0]] = patterns_test[key]
        #     else:
        #         patterns_target_test[key] = patterns_test[key] 

        target, nontarget = SPCA.cor(patterns_trenning, patterns_test_target, patterns_test_nontarget)
        self.nontarget = nontarget
        self.target = target
        ROC, AUC = SPCA.get_roc_auc_values(target, nontarget)
        if self.display_flag==False:
            display.display_auc(AUC)
            display.display_roc(ROC)

        self.sorted_auc = sorted(AUC.items(), key=operator.itemgetter(1), reverse=True)[:self.freqs_number]
        self.freqs_ = dict(self.sorted_auc).keys()

    def comput_classificator(self):
        target_to_class = []
        nontarget_to_class = []

        for f in self.freqs_:
            target_to_class.append(self.target[f])
            nontarget_to_class.append(self.nontarget[f])

        target_to_class = sum(target_to_class, [])
        nontarget_to_class = sum(nontarget_to_class, [])
        # import matplotlib.pyplot as plt
        # plt.hist(target_to_class)
        # plt.hist(nontarget_to_class)
        # plt.show()
        label = sum([[0]*len(nontarget_to_class), [1]*len(target_to_class)], [])
        data = np.array(sum([nontarget_to_class, target_to_class], []))
        gnb = GaussianNB()
        gnb.fit(data.reshape(len(data), 1), label)
        return gnb


    def create_config(self):
        values = {}
        values['freq'] = ';'.join([str(i) for i in self.freqs_])
        values['auc'] = []
        
        values['nontarget'] = self.nontarget
        values['target'] = self.target
        values['csp_montage'] = self.csp.P[:,0]
        values['patterns'] = {str(freq): self.signal_pattern_trenning_[str(freq)] for freq in self.freq_to_train}
        values['classyficator']  = self.comput_classificator()
        values['montage_matrix'] = self.montage_matrix
        values['channels_gains'] = self.channels_gains
        values['l_pattern'] = self.l_pattern
        values['use_channels']=';'.join(self._init_channels_names())
        values['leave_channels'] = ';'.join(self.leave_channels)
        values['montage_channels'] = ';'.join(self.montage_channels)
        return values

    def _signal_processing(self, signal): #self.channels_gains, self.montage_matrix  self.fs
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
        return signal

    def run(self):
        # compute csp
        self.csp = ComputeCSP(self.file_dir, self.file_name, 
                              self.l_trial, self.use_channels,
                              self.montage_type, self.montage_channels, 
                              self.tag_name, self.freq_to_train)

        self.csp.calculate()
        self.csp_montage = self.csp.P[:,0]

        #1. signal processing...
        #********************************************************************* 
        smart_tags_trenning = self._signal_segmentation(self.mgr, 2, 
                                                    0, self.tag_name)
        print self.l_trial-self.l_train-1
        print self.l_trial-(self.l_trial-self.l_train-1)

        smart_tags_test = self._signal_segmentation(self.mgr, self.l_trial-(self.l_trial-self.l_train-1), 
                                                    2, self.tag_name)
        

        for ind in xrange(len(smart_tags_trenning)):
            signal_trenning = self._signal_processing(smart_tags_trenning[ind].get_samples())            
            signal_test = self._signal_processing(smart_tags_test[ind].get_samples())

            smart_tags_trenning[ind].set_samples(signal_trenning, sum([[self.csp_channel_name], self.leave_channels], []))
            smart_tags_test[ind].set_samples(signal_test, sum([[self.csp_channel_name], self.leave_channels], []))

        self.all_channels = sum([[self.csp_channel_name], self.leave_channels], [])


        self.signal_pattern_test_target = {str(f):[] for f in self.freq_to_train}
        self.signal_pattern_test_nontarget = {str(f):[] for f in self.freq_to_train}
        self.signal_pattern_trenning = {str(f):[] for f in self.freq_to_train}
        for ind in xrange(len(smart_tags_trenning)):
            temp = Patterns(smart_tags_trenning[ind].get_samples(), self.l_pattern, self.csp_channel_name, self.leave_channels, sum([[self.csp_channel_name], self.leave_channels], []), self.fs)
            freqs = ast.literal_eval(smart_tags_trenning[ind].get_tags()[0]['desc']['freqs'])
            freq = freqs[self.active_field]
            self.signal_pattern_trenning[freq].append(temp.calculate()[1][self.active_field])

            temp = Patterns(smart_tags_test[ind].get_samples(), self.l_pattern, self.csp_channel_name, self.leave_channels, sum([[self.csp_channel_name], self.leave_channels], []), self.fs)
            freqs = ast.literal_eval(smart_tags_test[ind].get_tags()[0]['desc']['freqs'])
            freq = freqs
            temp2 = temp.calculate()[1]
            self.signal_pattern_test_target[freq[self.active_field]].append(temp2[self.active_field])
            self.signal_pattern_test_nontarget[freq[self.active_field]].append(([freq[i] for i in [0,1,2,3,4,5,6,7] if i!=self.active_field], [temp2[i] for i in [0,1,2,3,4,5, 6,7] if i!=self.active_field]))

        self.signal_pattern_trenning_ = {}
        for f in self.signal_pattern_trenning.keys():

            self.signal_pattern_trenning_[f] = np.mean(np.array(self.signal_pattern_trenning[f]), axis=0)

        self.calibration_trainer(self.signal_pattern_trenning_, self.signal_pattern_test_target, self.signal_pattern_test_nontarget )

        cfg = self.create_config()
        return cfg

if __name__ == '__main__':
    calib = ComputeCalibration('ssvep_pattern_8111723_calibration', '~/', '~/', 'aaaa')
    values = calib.run()
    with open(os.path.expanduser(os.path.join('~/', 'aaaa'+'_2')), 'wb') as handle:
        pickle.dump(values, handle)
