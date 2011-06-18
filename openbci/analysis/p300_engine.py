#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from openbci.core import  core_logging as logger
from openbci.offline_analysis.obci_signal_processing.signal import read_manager, read_info_source, read_data_source
from openbci.offline_analysis.obci_signal_processing.tags import read_tags_source
LOGGER = logger.get_logger("P300_engine", "debug")
import random, scipy
from offline_analysis.p300 import chain_analysis_offline as my_tools
from PyML import *
class P300Decision(object):
    def __init__(self, classifier):
        self.classifier = classifier

    def process(self, mgrs):
        row_mgrs = [m for m in mgrs if int(mgr.get_param('epoch_name'))<= 5]
        col_mgrs = [m for m in mgrs if int(mgr.get_param('epoch_name')) > 5]
        
        col_value = -1
        col = -1
        for i, mgr in enumerate(col_mgrs):
            dec, v = self.classifier.classify(mgr.get_samples(), 0)
            if v > 0 and v > col_value:
                col_value = v
                col = int(mgr.get_param('epoch_name')) - 5

        row = -1
        row_value = -1
        for i, mgr in enumerate(row_mgrs):
            dec, v = self.classifier.classify(mgr.get_samples(), 0)
            if v > 0 and v > row_value:
                row_value = v
                row = int(mgr.get_param('epoch_name'))

        return (col, row)

        

class P300Engine(object):
    def __init__(self, sampling, channels_names, blinks_size):
        self.channels_names = channels_names
        self.sampling = sampling
        self.blinks_size
        self.chain_elements = [
            my_tools.Segment(classes=[str(i) for i in range(12)],
                             start_offset=-0.2,
                             duration=0.4),
            my_tools.Average(bin_selectors=[str(i) for i in range(12)],
                             bin_names=[str(i) for i in range(12)],
                             size=self.blinks_size,
                             baseline=0.0,
                             strategy='random'),
            my_tools.Downsample(factor=3),
            my_tools.Normalize(norm=2),
            P300Decision(my_tools.SVM(C=3,
                                      Cmode='classProb',
                                      kernel=ker.Linear())
                         )
            ]
            
                             
                             

    def get_decision(self, blinks, samples):
        result = [self._get_mgr(blinks, samples)]
        for elem in self.chain_elements:
            result = elem.process(result)

        col = result[0]
        row = result[1]
        if col < 0 or row < 0:
            return -1
        else:
            return (row*6) + col

        return result

    def _get_mgr(self, blinks, samples):
        #create info
        info_source = read_info_source.MemoryInfoSource(
            {'sampling_frequency':str(float(self.sampling)),
             'channels_names':self.channels_names})
        first_sample_ts = samples[0][0].timestamp

        #create tags
        tags = []
        for b in blinks:
            tags.append({'start_timestamp':b.timestamp - first_sample_ts,
                         'end_timestamp':b.timestamp - first_sample_ts,
                         'name':str(b.index),
                         'channels':"",
                         'desc':{}
                         })
        tags_source = read_tags_source.MemoryTagsSource(tags)

        #create samples
        samples = scipy.array(
            [[s.value for channel.samples] for channel in samples])
        
        data_source = read_data_source.MemoryDataSource(samples)
        return read_manager.ReadManager(
            info_source,
            data_source,
            tags_source)
        

        

