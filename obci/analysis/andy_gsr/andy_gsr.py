#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os
import numpy as np
#sys.path.insert(1, '/home/mati/obci/')
from obci.acquisition import csv_manager
import csv as CCC

from obci.analysis.obci_signal_processing.tags import smart_tag_definition
from obci.analysis.obci_signal_processing import smart_tags_manager
from obci.analysis import offline_analysis_logging as logger
from obci.analysis.obci_signal_processing import read_manager
from obci.analysis.obci_signal_processing.signal import data_write_proxy
LOGGER = logger.get_logger("andy_gsr", "debug")

def exp_dat_csv(p_files):

    for f in p_files:
        csv = csv_manager.Writer(f['tags']+'.exp_data.csv', d=';', q=CCC.QUOTE_NONE)
        mgr = read_manager.ReadManager(f['info'], f['data'], f['tags'])
        tags = mgr.get_tags(p_tag_type='word')
        
        csv.write_row(['id', 'block_index','corr','rt','condition'])
        for t in tags:
            csv.write_row([f['info'][f['info'].rfind('/')+1:f['info'].find('.')],t['desc']['block_index'], t['desc']['corr'], t['desc']['rt'], t['desc']['condition']])
        csv.close()
        
def gsr_dat_csv(files):
    for f in files:
        print("START GSR FOR "+str(f)+"#############################################################")
        csv = csv_manager.Writer(f['tags']+'.gsr.csv', d=';', q=CCC.QUOTE_NONE)
        csv.write_row(['id', 'block_index','condition', 'gsr','gsr-base', 'gsr/base'])
        mgr = read_manager.ReadManager(f['info'], f['data'], f['tags'])
        sig = mgr.get_samples()
        tags = mgr.get_tags(p_tag_type='word')
        sf = float(mgr.get_param("sampling_frequency"))
        gain = float(mgr.get_param('channels_gains')[0])
        offset = float(mgr.get_param('channels_offsets')[0])

        bs_tag = mgr.get_tags(p_tag_type='baseline')[0]
        bs_raw = mgr.get_samples((bs_tag['start_timestamp']+7.0)*sf, (bs_tag['end_timestamp']-bs_tag['start_timestamp'])*sf)[0]
        bs_unit = bs_raw*gain + offset
        bs_avg = np.average(bs_unit)
        print("GAIN / OFFSET / SF / BS_AVG / sig_len:")
        print(gain, offset, sf, bs_avg, len(sig[0]))

        curr_block = 0
        last_ind = 0
        start_ts = tags[0]['start_timestamp']
        prev_tag = tags[0]
        for i, t in enumerate(tags[1:]):
            if int(t['desc']['block_index']) != curr_block:
                print("How many tags?: "+str(i-last_ind))
                last_ind = i
                
                print("Signal to grab: from: "+str(start_ts) +"len: "+str(prev_tag['end_timestamp'] - start_ts))
                signal_start = int(start_ts*sf)
                signal_len = int((prev_tag['end_timestamp'] - start_ts)*sf)
                print("Signal to grab in samples: from: "+str(signal_start) +"len: "+str(signal_len))
                gsr = np.average(mgr.get_samples(signal_start, signal_len)[0]*gain + offset)
                print("GSR!!!!!!!!!!!!!!!!: "+str(gsr))
                print(mgr.get_samples(signal_start, signal_len)[0]*gain + offset)
                gsr_base = gsr - bs_avg
                gsrbase = gsr/bs_avg

                csv.write_row([f['info'][f['info'].rfind('/')+1:f['info'].find('.')],
                               t['desc']['block_index'], t['desc']['condition'], 
                               gsr,
                               gsr_base,
                               gsrbase
                               ])
                
                

                start_ts = t['start_timestamp']
                curr_block = int(t['desc']['block_index'])
            prev_tag = t

        csv.close()

    
def run(files):
    exp_dat_csv(files)
    gsr_dat_csv(files)

if __name__ == "__main__":
    dr = '/media/data/eeg_data/dane_andy/'
    f_names = ['dawid_11_07_2012']#['daniel_11_07_2012', 'agnes_11_07_2012', 'cris_12_07_2012', 'lina_10_07_2012', 'piotr_12_07_2012', 'stefan_10_07_2012', 'zuzia_20_07_2012']#, 'Justyna', 'Kamila1', 'Kasia'] 'dawid_11_07_2012' 'maciek_11_07_2012',
    files = []
    for f_name in f_names:
        f = {
            'info': os.path.join(dr, f_name+'.obci.xml'),
            'data': os.path.join(dr, f_name+'.obci.raw'),
            'tags':os.path.join(dr, f_name+'.obci.tag')
            }
        files.append(f)
    run(files)





        
