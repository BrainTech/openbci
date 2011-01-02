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

import sys
#export PYTHONPATH=../../../:../../../openbci/:PYTHONPATH
sys.path.insert(1, '../../')
sys.path.insert(1, '../../openbci/')

import os.path
import math
from data_storage import read_manager
from core import core_logging as logger
LOGGER = logger.get_logger("lost_samples_test", "debug")


TEST = False

def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")

def find_lost_samples(p_read_mgr, numbers=None):
    """
    p_read_mgr['SAMPLE_NUMBER'] channels (or a collection numbers) 
    should contain a sequence of naturals (starting from 1)
    Check it and return all missing values.

    >>> find_lost_samples(None, [2,3,4,10,15,16,17,18,20])
    [1, 5, 6, 7, 8, 9, 11, 12, 13, 14, 19]

    """
    if p_read_mgr:
        samples_no = p_read_mgr.get_channel_samples("SAMPLE_NUMBER")
        print "NUMBER OF SAMPLES RED: "+str(len(samples_no))
    else:
        samples_no = numbers

    last = samples_no[0]
    lost = []
    lost += [i for i in range(1,int(last))]
    for no in samples_no[1:]:
        if (no - 1) != last:
            lost += [i for i in range(last+1, no)]
        last = no
    return lost
        
def print_result(l):
    """
    >>> print_result([])
    All samples were written.

    >>> print_result([1,2,3,4,5])
    All but first 5 samples were written.

    >>> print_result([1,2,10,11,15])
    Samples numbers that were NOT written:
    [1, 2, 10, 11, 15]

    """

    if len(l) == 0:
        print("All samples were written.")
    else:
        for i, v in enumerate(l):
            if i+1 == v:
                continue
            else:
                break
        if len(l[i+1:]) == 0:
            print ("All but first "+str(i+1)+" samples were written.")
        else:
            print ("Samples numbers that were NOT written:")
            print l
    


if __name__ == "__main__":
    
    if TEST:
        test()
        sys.exit(0)

    if len(sys.argv) == 3:
        f = {}
        f['info'] = sys.argv[1]
        f['dat'] = sys.argv[2]
    else:
        dr = '/media/windows/titanis/bci/projekty/eksperyment_mikolaj/dane_07_12_2010/201/'
        f_name = 'test2-Tue_Dec__7_14_03_55_2010'
        f = {
            'info': os.path.join(dr, f_name+'.obci.info'),
            'data': os.path.join(dr, f_name+'.obci.dat'),
            #'tags':os.path.join(dr, f_name+'.obci.tags')
            }
    read_manager = read_manager.ReadManager(
        f['info'],
        f['data'],
        None#f['tags']
        )

    l = find_lost_samples(read_manager)
    print_result(l)
            
            
        
