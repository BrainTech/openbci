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
import os, os.path, sys
from classification import chain as my_chain
from offline_analysis.p300 import chain_analysis_offline as my_tools
def run(files, folds=3, avg_size=10):
    ch = my_chain.Chain(
        my_chain.ChainElement(my_tools.ReadSignal,
                              {'files':[files]}),
        #my_chain.ChainElement(my_tools.ExcludeChannels,
        #                      {'channels':[#['SAMPLE_NUMBER', 'F8'],
        #                                   ['SAMPLE_NUMBER', 'F8', 'M1', 'M2']
        #                                   ]
        #                       }),

        #my_chain.ChainElement(my_tools.Plot,
        #                      [{'channel':'Pz'}]),

        my_chain.ChainElement(my_tools.Montage,
                              [
                {'montage_type': 'no_montage'},
                #{'montage_type': 'common_spatial_average'},
                {'montage_type': 'ears',
                'l_ear_channel': 'M1',
                'r_ear_channel': 'M2'}
                ]),
        my_chain.ChainElement(my_tools.LeaveChannels,
                              {'channels':[['Cz'],
                                           ['C3'],
                                           ['C4'],
                                           ['Fz'],
                                           ['Pz'],
                                           ]
                               }),
        my_chain.ChainElement(my_tools.Filter,
                [{'wp':0.3, 'ws':0.1, 'gpass': 3.0,
                  'gstop': 30.0, 'ftype':'cheby2', 'unit':'hz'}]),
        my_chain.ChainElement(my_tools.Filter,
                [{'wp':15.0, 'ws':25.0, 'gpass': 1.0,
                  'gstop': 60.0, 'ftype':'ellip', 'unit':'hz'}]),

        my_chain.ChainElement(my_tools.Segment,
                              {'classes':[('target','non-target')],
                               'start_offset':[-0.2, -0.1, 0.0, 0.1, 0.15],
                               'duration':[0.4, 0.5, 0.6]}),
        my_chain.ChainElement(my_tools.Average,
                              {'bin_selectors':[
                    [lambda mgr: mgr['name'] == 'target',
                     lambda mgr: mgr['name'] == 'non-target']],
                               'bin_names':[['target', 'non-target']],
                               'size':[avg_size],
                               'baseline':[0.0, 0.1, 0.2],
                               'strategy':['random']}),
        my_chain.ChainElement(my_tools.Downsample, # odwrotnie?
                              {'factor':[2, 3, 4, 5,7,9]}),
        my_chain.ChainElement(my_tools.Normalize,
                              {'norm': [2]}),
        my_chain.ChainElement(my_tools.PrepareTrainSet,
                              {}),
        my_chain.ChainElement(my_tools.SVM,
                              {'C': [1.0, 3.0, 5.0, 10.0],
                               'Cmode':['classProb'],
                               'folds':[folds],
                               'kernel':[ker.Linear()]
                               })                              
        )
    cs, res = ch.process(None, True, True)
    
    #now make svm better
    ret = files
    for elem in cs[:-1]:
        ret = elem.process(ret)
    new_ch = my_chain.Chain(
        my_chain.ChainElement(my_tools.SVM,
                              {'C':[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 12.0, 15.0, 20.0],
                               'Cmode':['classProb'],
                               'folds':[folds],
                               'kernel':[ker.Gaussian(1.0), ker.Gaussian(3.0), ker.Gaussian(5.0), ker.Gaussian(7.0), ker.Gaussian(10.0), 
                                         ker.Gaussian(2.0), ker.Gaussian(4.0), ker.Gaussian(5.0), ker.Gaussian(8.0), ker.Gaussian(11.0), 
                                         ker.Gaussian(12.0), ker.Gaussian(15.0), ker.Gaussian(18.0), ker.Gaussian(20.0), ker.Gaussian(25.0), 
                                         ker.Polynomial(3), ker.Polynomial(2), ker.Linear()]
                               })                              
        )

    new_cs, new_res = new_ch.process(ret, True, True)    
    cs[-1] = new_cs[-1]

    print("#############################################")
    print("CANDIDATES LEN: "+str(len(ch.candidates)))
    print("#############################################")
    ch.print_errors()
    ch.print_candidate(cs)
    print("#############################################")
    print("RESULT1: "+str(res))
    print("RESULT2: "+str(new_res))
    return cs, new_res
        
      

import sys
import p300_sample_data
if __name__ == '__main__':
    
    person = sys.argv[1]
    mode = sys.argv[2]
    folds = int(sys.argv[3])
    avg_size = int(sys.argv[4])

    files = p300_sample_data.get_files(person, mode)
    cs, res = run(files, folds, avg_size)

    cs[-1].ret = 'result'
    
    r = files
    for elem in cs:
        r = elem.process(r)
        

    ch = my_chain.Chain()
    ch.print_candidate(cs)
    print("Training/Testing result: "+str(res)+"/"+(str(r.getBalancedSuccessRate())))
    for i in range(cs[-1].folds):
        print("##########")
        print(r[i])
    print("*******")
    print(r)
    r.plotROC()
