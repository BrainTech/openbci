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
LOGGER = logger.get_logger("kamil_erp", "debug")


class KamilOddballExpTag(trigger_experiment.ExperimentTag):
    def get_name(self):
        #return self.group[:3]
        if self.word == 'drewno':
            return 'drewno'
        if self.group[:3] == 'Neu':
            return 'Neu'
        else:
            return self.group[0]
    def get_desc(self):
        return {
            'word':self.word,
            'fix_time':self.fix_time,
            'response':self.__dict__['t_resp.rt_raw'],
            'onset_time':self.onset_time_raw
            }

class KamilOddballFullExpTag(trigger_experiment.ExperimentTag):
    def get_name(self):
        if self.word == 'Drewno':
            return 'Drewno'
        else:
            return self.group

    def get_desc(self):
        return {
            'word':self.word,
            'fix_time':self.fix_time,
            'response':self.__dict__['t_resp.rt_raw'],
            'onset_time':self.onset_time_raw
            }

START_SEC_OFFSET = -0.1
DURATION = 1.0
NEG1_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name=u'N1', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
NEG3_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name=u'N3', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)


NEU1_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='Neutr1', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
NEU3_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='Neutr2', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)

POS1_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='P1', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
POS3_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='P3', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)


DREWNO_TAG_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='Drewno', 
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


    mgr_neu1 = smart_tags_manager.SmartTagsManager(NEU1_TAG_DEF, p_files['info'], p_files['data'], p_files['tags'])
    mgr_neu1.kamil_desc = "Neutr1"

    mgr_neu3 = smart_tags_manager.SmartTagsManager(NEU3_TAG_DEF, p_files['info'], p_files['data'], p_files['tags'])
    mgr_neu3.kamil_desc = "Neutr3"

    mgr_neg1 = smart_tags_manager.SmartTagsManager(NEG1_TAG_DEF, p_files['info'], p_files['data'], p_files['tags'])
    mgr_neg1.kamil_desc = "N1"

    mgr_neg3 = smart_tags_manager.SmartTagsManager(NEG3_TAG_DEF, p_files['info'], p_files['data'], p_files['tags'])
    mgr_neg3.kamil_desc = "N3"

    mgr_pos1 = smart_tags_manager.SmartTagsManager(POS1_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_pos1.kamil_desc = "P1"

    mgr_pos3 = smart_tags_manager.SmartTagsManager(POS3_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_pos3.kamil_desc = "P3"

    mgr_dr = smart_tags_manager.SmartTagsManager(DREWNO_TAG_DEF,  p_files['info'], p_files['data'], p_files['tags'])
    mgr_dr.kamil_desc = "Drewno"

    mgrs = []
    if plot_type == 'all':
        mgrs.append(mgr_neu1)
        mgrs.append(mgr_neu3)
        mgrs.append(mgr_neg1)
        mgrs.append(mgr_neg3)
        mgrs.append(mgr_pos1)
        mgrs.append(mgr_pos3)
        mgrs.append(mgr_dr)
    elif plot_type == 'system':
        mgr_pos1.kamil_desc = "Aut1 = P1+N1"
        mgr_pos1.get_smart_tags()
        mgr_pos1._smart_tags += mgr_neg1.get_smart_tags()
        mgrs.append(mgr_pos1)

        mgr_pos3.kamil_desc = "Refl3 = P3+N3"
        mgr_pos3.get_smart_tags()
        mgr_pos3._smart_tags += mgr_neg3.get_smart_tags()
        mgrs.append(mgr_pos3)

        mgr_neu1.kamil_desc = "Neu = Neu1+Neu3"
        mgr_neu1.get_smart_tags()
        mgr_neu1._smart_tags += mgr_neu3.get_smart_tags()
        mgrs.append(mgr_neu1)

        mgrs.append(mgr_dr)

    elif plot_type == 'sign':
        mgr_pos1.kamil_desc = "Pos = P1+P3"
        mgr_pos1.get_smart_tags()
        mgr_pos1._smart_tags += mgr_pos3.get_smart_tags()
        mgrs.append(mgr_pos1)

        mgr_neg1.kamil_desc = "Neg = N1+N3"
        mgr_neg1.get_smart_tags()
        mgr_neg1._smart_tags += mgr_neg3.get_smart_tags()
        mgrs.append(mgr_neg1)

        mgr_neu1.kamil_desc = "Neu = Neu1+Neu3"
        mgr_neu1.get_smart_tags()
        mgr_neu1._smart_tags += mgr_neu3.get_smart_tags()
        mgrs.append(mgr_neu1)

        mgrs.append(mgr_dr)
        

        

    #mgr_pos3.kamil_desc = "P3+N3"
    #mgr_pos3.get_smart_tags()
    #mgr_pos3._smart_tags += mgr_neg3.get_smart_tags()
    #mgrs.append(mgr_pos3)





    if channel_names is None:
        import math
        channel_names = [mgr_pos.get_param('channels_names')]
        x = int(math.sqrt(len(channels_names)))
        y = ceil(math.sqrt(len(channels_names)))


    for i, channels in enumerate(channel_names):

        plotter = erp_plot.Plotter(x, y, i)
        plt_id = 0
        for i_ch_name in channels:
            plt_id += 1
            for mgr in mgrs:
                avgs_for_channels = erp_avg.get_normalised_avgs(mgr, abs(START_SEC_OFFSET)*1024)*0.0715
                ch = get_channel_data(mgr_dr, avgs_for_channels, i_ch_name)
                if ch is None:
                    LOGGER.warning("Couldn`t find channel for name: "+i_ch_name)
                else:
                    samp = float(mgr.get_read_manager().get_param('sampling_frequency'))
                    plotter.add_plot(ch, 
                                     mgr.kamil_desc+" "+i_ch_name, 
                                     [i for i in range(START_SEC_OFFSET*samp-1, len(ch)-(abs(START_SEC_OFFSET)*samp))],
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
        #my_chain.ChainElement(my_tools.Filter,
        #                      [{'wp':[0.5, 30], 'ws':[0.1, 45.0], 'gpass': 5.0,
        #                        'gstop': 40.0, 'ftype':'cheby2', 'unit':'hz', 'use_filtfilt':False}]),
        #my_chain.ChainElement(my_tools.Filter,
        #                      [{'wp':0.8, 'ws':0.2, 'gpass': 2.0,
        #                        'gstop': 60.0, 'ftype':'ellip', 'unit':'hz', 'use_filtfilt':True}]),
        my_chain.ChainElement(my_tools.Filter,
                              [{'wp':20.0, 'ws':30.0, 'gpass': 5.0,
                                'gstop': 60.0, 'ftype':'cheby2', 'unit':'hz', 'use_filtfilt':True}]),
        my_chain.ChainElement(my_tools.SaveToFile,
                              [{'dir_path':dr,
                                'file_name':f_name}])
        )
    cs, res = ch.process(None, False, False)
                              

def run(p_files, plot_type='all', p_show=True):
    plot_avgs_for(p_files, plot_type, p_show, 2, 3, [['Fp1', 'Fpz', 'Fp2', 'F3', 'Fz', 'F4'], ['P3', 'Pz', 'P4', 'C3', 'Cz', 'C4']])

def fix_file(f, from_sample, num_of_samples, sample_value):
    mgr = read_manager.ReadManager(f['info'], f['data'], None)
    wr = data_file_proxy.DataFileWriteProxy(f['data']+'.fixed.raw')
    for i, s in enumerate(mgr.iter_samples()):
        for v in s:
            wr.data_received(v)
        if i > from_sample:
            print("BREAK")
            break


    ch_no = int(mgr.get_param('number_of_channels'))
    for i in range(num_of_samples):
        for j in range(ch_no):
            wr.data_received(sample_value)
    print("FILLED")
    

    for i, s in enumerate(mgr.iter_samples()):
        if i > from_sample:
            for v in s:
                wr.data_received(v)

    wr.finish_saving()


    

    

if __name__ == "__main__":
    dr = '/media/windows/titanis/bci/projekty/eksperyment_kamil/eeg-eksperyment-20-05-2011marysia/'

    #f_name = 'Agata'
    #f_csv_name = 'Agata_Feb_25_1229.csv'
    #f_name = 'Justyna'
    #f_csv_name = 'Justyna_Feb_25_1113.csv'
    #f_name = 'Kamila1'
    #f_csv_name = 'Kamila1_Feb_25_1404.csv'
    #f_name = 'Kasia'
    #f_csv_name = 'Kasia_Feb_25_0925.csv'
    #f_name = 'Linda'
    #f_csv_name = 'Linda_Feb_25_1501.csv'
    f_names = ['marysia_18_05_2011']#, 'Agata', 'Justyna', 'Kamila1', 'Kasia']
    for f_name in f_names:
        f = {
            'info': os.path.join(dr, f_name+'.xml'),
            'data': os.path.join(dr, f_name+'.filtered2.raw.obci.dat'),
            'tags':os.path.join(dr, f_name+'.obci.fixed.arts_free.tags')
            }
        #lost_samples_test.find_and_print(f['info'], f['data'])
        #fix_file(f, from_sample=2701686-870572, num_of_samples=28877, sample_value=0.0)
        #trigger_experiment.trigger_to_tag(f['tags'], dr+f_name+'.csv', f['info'], f['data']+'.fixed.raw', KamilOddballFullExpTag, 2, 1, 1.0, 0.3)
        #filter_and_store(f, dr, f_name+'.filtered2.raw')
        run(f, plot_type='system')





        
