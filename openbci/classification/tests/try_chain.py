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
def run():
    dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/squares/'
    f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_longer_8trials2'
    f2 = {
        'info': os.path.join(dr2, f2_name+'_10HZ.obci.xml'),
        'data': os.path.join(dr2, f2_name+'_10HZ.obci.bin'),
        'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
       }
    
    """dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/numbered_squares/'
    f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBERS_CATDOGFISHWATERBOWL_longer_8trials'
    f2 = {
        'info': os.path.join(dr2, f2_name+'.obci.filtered.xml'),
        'data': os.path.join(dr2, f2_name+'_10HZ.obci.bin'),
        'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
       }"""

    train_data_ch, train_labels = prepare.get_train_set(f2, num_per_avg=15, start_samples_to_norm=0, downsample_level=5) 
    class MY_SVM(object):
        def __init__(self, C):
            self.s = svm.SVM(C=C)
        def process(self, data):
            return self.s.stratifiedCV(data, 5).getBalancedSuccessRate()
        def __repr__(self):
            return "SVM: C - "+str(self.s.C)

    class MY_STD(object):
        def process(self, data):
            #p = prepare.Standardizer()
            #p.train(data)
            data.normalize(2)
            return data

    ch = my_chain.Chain(
        my_chain.ChainElement(MY_STD, {}),
        my_chain.ChainElement(MY_SVM,
                              {'C':[0.01, 0.1, 0.5, 1, 10]})
        )

    l = Labels([str(i) for i in train_labels])
    for i, train_data in enumerate(train_data_ch):
        train_data = train_data_ch[11]
        data = VectorDataSet(train_data, L=l)
        cs, res = ch.process(data)
        print("CSS: "+str(cs))
        print("RES: "+str(res))
        break
if __name__ == '__main__':
    run()
