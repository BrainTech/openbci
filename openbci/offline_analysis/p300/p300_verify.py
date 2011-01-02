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
from offline_analysis.p300 import analysis_offline

def run_verification(chain, folds, non_target_per_target):
    ret = None
    c = chain[-1]
    for elem in chain[:-2]:
        ret = elem.process(ret)

    succ, stats = analysis_offline.p300_verify_svm(
        ret, c.C, c.Cmode, c.kernel,
        folds, non_target_per_target)
    print
    print("#############################################")
    print("RESULT SUCCESS RATE: "+str(succ))
    print("#############################################")
    print("For every fold:")
    for st in stats:
        print("SUCC NUM: "+str(st[0])+" | FAIL NUM: "+str(st[1]))
    print("#############################################")
    print("RESULT SUCCESS RATE: "+str(succ))
    print("#############################################")


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

        
    
import p300_sample_data
import sys
if __name__ == '__main__':
    
    person = sys.argv[1]
    mode = sys.argv[2]
    folds = int(sys.argv[3])
    avg_size = int(sys.argv[4])
    action = sys.argv[5]
    if action == 'verify':
        run_verification(p300_sample_data.get_chain('bci_competition', 'A', avg_size), folds, 6)
    elif action == 'test':
        run_test(p300_sample_data.get_chain(person, mode, avg_size), folds)
             
             
