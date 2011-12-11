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
sys.path.insert(1, '../../../')
sys.path.insert(1, '../../../openbci/')

from offline_analysis import trigger_experiment
from openbci.tests import lost_samples_test
from offline_analysis.erp import erp_avg
from offline_analysis.erp import erp_plot
from openbci.offline_analysis.obci_signal_processing.tags import smart_tag_definition
from openbci.offline_analysis.obci_signal_processing import smart_tags_manager
from openbci.offline_analysis import offline_analysis_logging as logger
from openbci.offline_analysis.obci_signal_processing import read_manager
from openbci.offline_analysis.obci_signal_processing.signal import data_file_proxy
LOGGER = logger.get_logger("mati_p300_ssvep", "debug")


START_SEC_OFFSET = -0.1
DURATION = 1.0
BLINK_70HZ_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='blinkSSVEP70', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
BLINK_15HZ_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='blinkSSVEP15', 
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
    mgr_15 = smart_tags_manager.SmartTagsManager(BLINK_15HZ_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_15.kamil_desc = "blink_15Hz"

    mgr_70 = smart_tags_manager.SmartTagsManager(BLINK_70HZ_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_70.kamil_desc = "blink_70Hz"

    mgrs = []
    if plot_type == 'all':
        mgrs.append(mgr_15)
        mgrs.append(mgr_70)

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
            for mgr in mgrs:
                samp = float(mgr.get_read_manager().get_param('sampling_frequency'))
                avgs_for_channels = erp_avg.get_normalised_avgs(mgr, abs(START_SEC_OFFSET)*samp)*0.0715
                ch = get_channel_data(mgr, avgs_for_channels, i_ch_name)
                if ch is None:
                    LOGGER.warning("Couldn`t find channel for name: "+i_ch_name)
                else:
                    LOGGER.debug("ADD PLOT: "+mgr.kamil_desc+" "+i_ch_name,)
                    #[i for i in range(START_SEC_OFFSET*samp-1, len(ch)-(abs(START_SEC_OFFSET)*samp))]
                    labels = [i*1000/samp for i in range(START_SEC_OFFSET*samp-1, len(ch)-(abs(START_SEC_OFFSET)*samp))]
                    plotter.add_plot(ch, 
                                     mgr.kamil_desc+" "+i_ch_name, 
                                     labels,
                                     plt_id)
                #store_avgs_for_svarog([ch])
        plotter.prepare_to_show()
    if p_show:
        erp_plot.show()

from classification import chain as my_chain
from offline_analysis.p300 import chain_analysis_offline as my_tools

def filter_and_store(files, dr, f_name):
    ch = my_chain.Chain(
        my_chain.ChainElement(my_tools.ReadSignal,
                              [{'files':[files]}]),
        my_chain.ChainElement(my_tools.Montage,
                              [{'montage_type':'ears',
                                'l_ear_channel':'M2', 'r_ear_channel':'M2'}]),
        my_chain.ChainElement(my_tools.Filter,
                              [{'wp':0.1, 'ws':0.03, 'gpass': 3.0,
                                'gstop': 10.81, 'ftype':'butter', 'unit':'hz', 'use_filtfilt':True}]),
        my_chain.ChainElement(my_tools.Filter,
                              [{'wp':30.0, 'ws':60.0, 'gpass': 3.0,
                                'gstop': 14.91, 'ftype':'butter', 'unit':'hz', 'use_filtfilt':True}]),
        my_chain.ChainElement(my_tools.SaveToFile,
                              [{'dir_path':dr,
                                'file_name':f_name}])
        )
    cs, res = ch.process(None, False, False)
                              

def run(p_files, plot_type='all', p_show=True):
    plot_avgs_for(p_files, plot_type, p_show, 2, 3, [['P3', 'Pz', 'P4', 'C3', 'Cz', 'C4'],['O1', 'O2', 'FCz', 'Fp1', 'Fz', 'Fp2']])

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





        
