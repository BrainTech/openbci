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
from data_storage import signalml_read_manager
from core import core_logging as logger
LOGGER = logger.get_logger("lost_samples_test", "debug")


TEST = True

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
        samples_no = p_read_mgr.get_channel_values("SAMPLE_NUMBER")
    else:
        samples_no = numbers

    last = samples_no[0]
    lost = []
    lost += [i for i in range(1,last)]
    for no in samples_no[1:]:
        if (no - 1) != last:
            lost += [i for i in range(last+1, no)]
        last = no
    return lost
        
    


if __name__ == "__main__":
    
    if TEST:
        test()
        sys.exit(0)

    dr = '/home/mati/bci_dev/google_openbci/openbci/temp/'
    f_name = 'test_trigger10_09_11_2010_c++usb_svarog_22channels_512Hz'
    f = {
        'info': os.path.join(dr, f_name+'.obci.info'),
        'data': os.path.join(dr, f_name+'.obci.dat'),
        'tags':os.path.join(dr, f_name+'.obci.tags')
       }
    read_manager = signalml_read_manager.SignalmlReadManager(
        f['info'],
        f['data'],
        f['tags'])
    read_manager.start_reading()
    find_lost_samples(read_manager)
