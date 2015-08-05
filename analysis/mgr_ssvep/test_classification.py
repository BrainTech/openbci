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

# import numpy as np

# import pickle

from obci.analysis.obci_signal_processing import read_manager

# import signal_processing.filters as SPF
import signal_processing.parse_signal as SPPS
# import signal_processing.montage_signal as SPSM
# import signal_processing.csp_analysis as SPCSP
# import signal_processing.calibration_analysis as SPCA

# from data_analysis.compute_pattern2 import ComputePattern

# import data_analysis.display as display

from classification_ssvep_pattern import ClassificationSsvepPattern


CHANNELS_TO_IGNORE = [u'Dioda1',u'Dioda2',u'Dioda3',u'Dioda4',
                      u'Dioda5',u'Dioda6',u'Dioda7',u'Dioda8',
                      u'AmpSaw', u'DriverSaw']

CHANNELS_TO_MONTAGE = [u'PO7']

CHANNELS_TO_LEAVE = [u'Dioda1',u'Dioda2',u'Dioda3',u'Dioda4',
                     u'Dioda5',u'Dioda6',u'Dioda7',u'Dioda8']

MONTAGE_TYPE = 'diff'

FREQ_TO_TRAIN = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]

class TestClassification(object):
    def __init__(self, file_name, file_dir, config_file_dir, config_file_name, 
                 l_trial=4,
                 l_train=2,
                 ignore_channels=CHANNELS_TO_IGNORE,
                 montage_type=MONTAGE_TYPE, 
                 montage_channels=CHANNELS_TO_MONTAGE, 
                 leave_channels=CHANNELS_TO_LEAVE, 
                 tag_name=u'diodes', 
                 freq_to_train=FREQ_TO_TRAIN, 
                 active_field=5,
                 display_flag=False,
                 l_pattern=1,
                 l_buffer_trenning=2):

        super(TestClassification, self).__init__()
        self.file_dir = file_dir
        self.file_name = file_name
        self.mgr = self._init_read_manager()
        self.fs = float(self.mgr.get_param("sampling_frequency"))
        self.all_channels = self.mgr.get_param('channels_names')
        self.channels_gains = self.mgr.get_param("channels_gains")

        self.classification = ClassificationSsvepPattern(config_file_dir, config_file_name,ignore_channels,
                 montage_type, 
                 montage_channels, 
                 leave_channels, 
                 self.all_channels,
                 self.channels_gains,
                 display_flag=False,
                 l_pattern=1,
                 sampling_frequency=self.fs)


        self.file_dir = file_dir
        self.file_name = file_name

        self.l_trial = l_trial
        self.l_train = l_train
        self.l_pattern = l_pattern
        self.l_buffer_trenning=l_buffer_trenning
        self.tag_name = tag_name
        self.freq_to_train = freq_to_train
        self.display_flag = display_flag


    def _init_read_manager(self):
        file_name = os.path.expanduser(os.path.join(self.file_dir, self.file_name))

        return read_manager.ReadManager(file_name+'.obci.xml', 
                                        file_name+'.obci.raw', 
                                        file_name+'.obci.tag')



    def _signal_segmentation(self, mgr, l_trial, offset, tag_name):
        return SPPS.signal_segmentation(mgr, l_trial, offset, tag_name)

    def run(self):
        smart_tags1 = self._signal_segmentation(self.mgr, self.l_trial-self.l_train-0.5, 
                                                    self.l_buffer_trenning-0.5, self.tag_name)
        smart_tags2 = self._signal_segmentation(self.mgr, self.l_trial-self.l_train+0.5, 
                                                    0, self.tag_name)
        w = []
        t = []
        for i in range(len(smart_tags1)):
            freqs = ast.literal_eval(smart_tags1[i].get_tags()[0]['desc']['freqs'])
            freqs2 = sum([freqs[4:],freqs[:4]], [])
            predictions = self.classification.run(smart_tags1[i].get_samples(), freqs2)


if __name__ == '__main__':
    test = TestClassification('dane_mgr_ania_2', '~/syg', '~/', 'aaaa_2')
    test.run()