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

import sys, os
import numpy
sys.path.insert(1, '../../../')
sys.path.insert(1, '../../../openbci/')

from offline_analysis import trigger_experiment
from openbci.tests import lost_samples_test
from offline_analysis.erp import ssvep_avg
from offline_analysis.erp import erp_plot
from openbci.offline_analysis.obci_signal_processing.tags import smart_tag_definition
from openbci.offline_analysis.obci_signal_processing import smart_tags_manager
from openbci.offline_analysis import offline_analysis_logging as logger
from openbci.offline_analysis.obci_signal_processing import read_manager
from openbci.offline_analysis.obci_signal_processing.signal import data_file_proxy
LOGGER = logger.get_logger("mati_p300_ssvep", "debug")


START_SEC_OFFSET = 0.0
DURATION = 8.0
BLINK_SSVEP_70HZ_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='trial_p300', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
BLINK_SSVEP_15HZ_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='trial_p300_ssvep', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
SSVEP_15HZ_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='trial_ssvep', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)

def get_channel_data(mgr, p_channels, p_channel_name):
    names = mgr.get_read_manager().get_param('channels_names')
    LOGGER.info("Channels names: "+str(names))
    ch_num = None
    for i, name in enumerate(names):
        if name == p_channel_name:
            ch_num = i
            break

    if ch_num is None:
        return None
    else:
        return p_channels[ch_num]


def plot_avgs_for(p_files, plot_type='all', p_show=True, x=None, y=None, channel_names=None):
    mgr_15 = smart_tags_manager.SmartTagsManager(BLINK_SSVEP_15HZ_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_15.kamil_desc = "15Hz+B"

    mgr_70 = smart_tags_manager.SmartTagsManager(BLINK_SSVEP_70HZ_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_70.kamil_desc = "B"

    mgr_no_15 = smart_tags_manager.SmartTagsManager(SSVEP_15HZ_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_no_15.kamil_desc = "15Hz"

    mgrs = []
    if plot_type == 'all':
        mgrs.append(mgr_15)
        #mgrs.append(mgr_70)
        mgrs.append(mgr_no_15)

    samp = float(mgr_70.get_read_manager().get_param('sampling_frequency'))        
    norm_avgs, freqs = ssvep_avg.get_normalised_avgs(
        samples_source=mgr_70,
        norm_array=None,
        norm_type='none',
        NFFT=samp, 
        Fs=samp, 
        noverlap=samp*3/4)

    avgs_for_channels = []
    for i, mgr in enumerate(mgrs):
        samp = float(mgr.get_read_manager().get_param('sampling_frequency'))
        avgs, freqs = ssvep_avg.get_normalised_avgs(
            samples_source=mgr,
            norm_array=norm_avgs,
            norm_type='divide',
            NFFT=samp, 
            Fs=samp, 
            noverlap=samp*3/4)
        avgs_for_channels.append(avgs)


    if channel_names is None:
        import math
        channel_names = [mgr_pos.get_param('channels_names')]
        x = int(math.sqrt(len(channel_names)))
        y = ceil(math.sqrt(len(channel_names)))

    LOGGER.debug("GO WITH CHANNELS: "+str(channel_names))
    for i, channels in enumerate(channel_names):

        plotter = erp_plot.Plotter(x, y, i)
        plt_id = 0
        LOGGER.debug("Finally with channels: "+str(channels))
        for i_ch_name in channels:
            plt_id += 1
            for x, mgr in enumerate(mgrs):
                ch = get_channel_data(mgr, avgs_for_channels[x], i_ch_name)
                if ch is None:
                    LOGGER.warning("Couldn`t find channel for name: "+i_ch_name)
                else:
                    LOGGER.debug("ADD PLOT: "+mgr.kamil_desc+" "+i_ch_name,)

                    labels = freqs
                    plotter.add_plot(ch, 
                                     mgr.kamil_desc, 
                                     labels,
                                     plt_id)
            plotter.add_plot_param(plt_id, 'title', i_ch_name)
            #ch = get_channel_data(mgr_70, norm_avgs, i_ch_name)
            #plotter.add_plot(ch, 
            #                 mgr_70.kamil_desc, 
            #                 freqs,
            #                 plt_id)

        plotter.prepare_to_show(xlabel='freq (HZ)', ylabel='PW', loc=2)
    if p_show:
        erp_plot.show()

def run(p_files, plot_type='all', p_show=True):
    plot_avgs_for(p_files, plot_type, p_show, 2, 3, [['Pz', 'C4', 'Cz', 'Fz', 'O1', 'O2']])

if __name__ == "__main__":
    dr = '/home/mati/dane/'
    f_names = ['osoba1']

    
    for f_name in f_names:
        f = {
            #'info': os.path.join(dr, f_name+'.xml'),
            #'data': os.path.join(dr, f_name+'.raw'),
            'info': os.path.join(dr, f_name+'.filtered.raw.obci.info'),
            'data': os.path.join(dr, f_name+'.filtered.raw.obci.dat'),
            'tags':os.path.join(dr, f_name+'.tag.fixed.tag')
            }
        #filter_and_store(f, dr, f_name+'.filtered.raw')
        run(f, plot_type='all')





        
