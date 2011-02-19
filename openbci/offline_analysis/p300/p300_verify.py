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
from PyML import *
from offline_analysis.p300 import p300_train_prepare_train_set as prepare
import scipy
import os, os.path, sys, math, random
from classification import chain as my_chain
from offline_analysis.p300 import chain_analysis_offline as my_tools
from offline_analysis.p300 import analysis_offline
from offline_analysis.erp import erp_plot

def run_verification(chain, folds, non_target_per_target):
    ret = None
    c = chain[-1]
    for elem in chain[:-2]:
        ret = elem.process(ret)

    succ, stats = analysis_offline.p300_verify_svm(
        ret, c.C, c.Cmode, c.kernel,
        folds, non_target_per_target)

    print("#############################################")
    print("RESULT SUCCESS RATE: "+str(succ))
    print("#############################################")
    print("For every fold:")
    for i in range(len(stats[0])):
        print("SUCC NUM: "+str(stats[0][i])+" | FAIL NUM: "+str(stats[1][i]))
    print("#############################################")
    print("RESULT SUCCESS RATE: "+str(succ))
    print("#############################################")
    return succ


def run_test(chain, folds):
    chain[-1].ret = 'result'
    chain[-1].folds = folds
    ret = None
    for elem in chain:
        ret = elem.process(ret)
    print("#############################################")
    print("Testing result: "+(str(ret.getBalancedSuccessRate())))
    for i in range(chain[-1].folds):
        print("##########")
        print(ret[i])
    print("*******")
    print(ret)
    ret.plotROC()


def run_plot(person1, mode1, person2, mode2, avg_sizes, channels):
    chain1 = p300_sample_data.get_chain(person1, mode1, 5)
    chain2 = p300_sample_data.get_chain(person2, mode2, 5)
    x = 1 # for now
    y = 1 # for now
    assert(len(channels) == 1) # for now


    mgrs1 = None
    mgrs2 = None
    # Filter
    for ch in [chain1[0], chain1[3], chain1[4]]:
        mgrs1 = ch.process(mgrs1)
    for ch in [chain2[0], chain2[3], chain2[4]]:
        mgrs2 = ch.process(mgrs2)

    # Segment
    segmenter = my_tools.Segment(classes=('target','non-target'), start_offset=-0.1, duration=0.6)
    mgrs1 = segmenter.process(mgrs1)
    mgrs2 = segmenter.process(mgrs2)


    averager = my_tools.Average(bin_selectors=[lambda mgr: mgr['name'] == 'target',
                                        lambda mgr: mgr['name'] == 'non-target'],
                                bin_names=['target', 'non-target'], size=5,
                                baseline=0.1, strategy='random')

    samp = float(mgrs1[0].get_param('sampling_frequency'))
    for i, avg_size in enumerate(avg_sizes):
        # Ommit reading-in : normalize, prepare, classify
        averager.size = avg_size
        avgs1 = averager.process(mgrs1)
        avgs2 = averager.process(mgrs2)

        plotter = erp_plot.Plotter(x, y, avg_size)
        plt_id = 0
        for i_ch_name in channels:
            plt_id += 1
            
            avgs = [] 
            for avg in avgs1:
                if avg.get_param('epoch_name') == 'target':
                    avg.name = '1 - target'
                    avgs.append(avg)
                    break
            for avg in avgs1:
                if avg.get_param('epoch_name') == 'non-target':
                    avg.name = '1 - non-target'
                    avgs.append(avg)
                    break
            for avg in avgs2:
                if avg.get_param('epoch_name') == 'target':
                    avg.name = '2 - target'
                    avgs.append(avg)
                    break
            for avg in avgs2:
                if avg.get_param('epoch_name') == 'non-target':
                    avg.name = '2 - non-target'
                    avgs.append(avg)
                    break


            for j, avg in enumerate(avgs):
                ch = avg.get_channel_samples(i_ch_name)*0.0715
                plotter.add_plot(ch, 
                                 avg.name+" - "+i_ch_name, 
                                 [i*(1/samp)*1000 for i in range(-0.1*samp-1, len(ch)-(0.1*samp))],
                                 plt_id, {'linewidth':2.0})
            
        plotter.prepare_to_show()
    erp_plot.show()


    
    
import p300_sample_data
import sys
if __name__ == '__main__':
    
    person = sys.argv[1]
    mode = sys.argv[2]
    action = sys.argv[5]
    if action == 'verify':
        folds = int(sys.argv[3])
        avg_size = int(sys.argv[4])
        try:
            reps = int(sys.argv[6])
        except:
            reps = 1
        res = 0.0
        for i in range(reps):
            res += run_verification(p300_sample_data.get_chain(person, mode, avg_size), folds, 6)

        print("**************************************")
        print("Aggregted SUCCESS RATE: "+str(res/reps))
    elif action == 'test':
        folds = int(sys.argv[3])
        avg_size = int(sys.argv[4])
        run_test(p300_sample_data.get_chain(person, mode, avg_size), folds)
    elif action == 'plot':
        #python openbci/offline_analysis/p300/p300_verify.py mati squares mati numbered_squares plot
        person2 = sys.argv[3]
        mode2 = sys.argv[4]
        run_plot(person, mode, person2, mode2, [5, 10, 15, 100], ['Cz'])
             
             
