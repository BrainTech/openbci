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

"""Implement averaged epochs class."""

from openbci.offline_analysis.obci_signal_processing import read_manager
from openbci.offline_analysis.obci_signal_processing.signal import read_info_source
from openbci.offline_analysis.obci_signal_processing.signal import read_data_source
from openbci.offline_analysis.obci_signal_processing.tags import read_tags_source
from offline_analysis.erp import erp_avg



class AveragedEpochs(read_manager.ReadManager):
    def __init__(self, p_mgrs, p_info_source, p_avg_name,
                 p_samples_to_norm=0, p_avg_len=None):
        avg_samples = erp_avg.get_normalised_avgs(p_mgrs, p_samples_to_norm, p_avg_len)
        tags_source = read_tags_source.MemoryTagsSource([])
        p_info_source.get_params()['epoch_name'] = p_avg_name
        samples_source = read_data_source.MemoryDataSource(avg_samples)
        super(AveragedEpochs, self).__init__(p_info_source,
                                      samples_source,
                                      tags_source)
        
