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

import os.path
import sys


# Set to true to run tests not using mx
TEST = False

if not TEST:
    try:
        from openbci.offline_analysis.obci_signal_processing import read_manager
        from core import core_logging as logger
        LOGGER = logger.get_logger("trigger_change", "debug")
    except ImportError, e:
        print(e)
        print("Set obci python path. If you are in current dir RUN: export PYTHONPATH=../../../:../../../openbci/:PYTHONPATH")
        sys.exit(1)

def get_trigger_sent_timestamps(p_read_mgr, p_asci_file_path=None):
    """
    Parameters:
    p_read_mgr - read manager with file with tags named 'trigger'
    or
    p_asci_file_path - a file with asci file with every line in format: 
                       start_trig_change(float) end_trig_change(float) trig_value(float)
    Return:
    a, b where:
    a - a list of subsequent trigger values
    b - a list of trigger send timestamps
    len(a) == len(b)

    TESTS:

    >>> from openbci.offline_analysis.obci_signal_processing import read_manager

    >>> mgr = read_manager.ReadManager('test_save_timestamp.obci.info', 'test_save_timestamp.obci.dat', 'test_save_timestamp.obci.tags')

    >>> get_trigger_sent_timestamps(mgr)
    ([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0], [1289219036.7517459, 1289219046.7608111, 1289219048.3307059, 1289219050.0087421, 1289219051.671896, 1289219053.2007921, 1289219054.699033, 1289219056.3630681, 1289219058.287384, 1289219060.1364889])


    >>> get_trigger_sent_timestamps(None, 'test_save_timestamp.asci_trigger')
    ([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0], [1289219036.7517459, 1289219046.7608111, 1289219048.3307059, 1289219050.0087421, 1289219051.671896, 1289219053.2007921, 1289219054.699033, 1289219056.3630681, 1289219058.287384, 1289219060.1364889])

    """

    ret_trig_values = []
    ret_trig_change_tss = []

    if p_read_mgr:
        tags = p_read_mgr.get_tags('trigger')
        for tag in tags:
            start = tag['start_timestamp']
            v = float(tag['desc']['value'])
            ret_trig_values.append(v)
            ret_trig_change_tss.append(start)
    else:
        f = open(p_asci_file_path, 'r')
        tss = []
        for l in f.readlines():
            start, end, v = l.strip().split(' ')
            ret_trig_values.append(float(v))
            ret_trig_change_tss.append(float(start))

    return ret_trig_values, ret_trig_change_tss


def get_trigger_received_timestamps(p_read_mgr, trig=None, tss=None):
    """
    Parameters:
    p_read_mgr - read manager with file with channels: "TIMESTAMPS" and "TRIGGER"
    or
    trig and tss - collections of trigger values and timestamps

    Return:
    a, b, c where:
    a - a list of subsequent trigger values
    b - a list of trigger change timestamps (b[0] is always first_value_timestamp)
    c - a list of same trigger value lengths (c[i] > 0 for every i)
    len(a) == len(b) == len(c)

    TESTS:

    >>> get_trigger_received_timestamps(None, [1,1,1,0,0,1,0,1,1,1,1,0], [i+22 for i in range(12)])
    ([1, 0, 1, 0, 1, 0], [22, 25, 27, 28, 29, 33], [3, 2, 1, 1, 4, 1])

    >>> get_trigger_received_timestamps(None, [1,1,1,1], [1,2,3,4])
    ([1], [1], [4])

    >>> from openbci.offline_analysis.obci_signal_processing import read_manager

    >>> mgr = read_manager.ReadManager('test_save_timestamp.obci.info', 'test_save_timestamp.obci.dat', 'test_save_timestamp.obci.tags')

    >>> get_trigger_received_timestamps(mgr)
    ([0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0], [1289219036.6731031, 1289219038.7224219, 1289219040.72524, 1289219042.731863, 1289219044.8221769, 1289219046.843883, 1289219049.156811, 1289219051.20767, 1289219053.24529, 1289219055.395386, 1289219057.4999781, 1289219059.658108, 1289219061.853564], [274, 253, 258, 291, 256, 304, 276, 279, 271, 287, 297, 289, 59])

    """

    if p_read_mgr:
        trig = p_read_mgr.get_channel_samples("TRIGGER")
        try:
            tss = p_read_mgr.get_channel_samples("TIMESTAMPS")
        except:
            print("Warning! No 'timestamps' channel found. Assumed ideal timing ...")
            sampling = float(p_read_mgr.get_param('sampling_frequency'))
            tss = [i/sampling for i in range(len(trig))]
        try:
            first = float(p_read_mgr.get_param('first_sample_timestamp'))
        except:
            print("Warning! No 'first_sample_timestamp' field found. Assumed 0...")
            first = 0.0

        tss = [(i-first) for i in tss]

    
    ret_trig_change_tss = [tss[0]]
    ret_trig_values = [trig[0]]
    ret_trig_change_lens = []
    tr_prev = trig[0]
    tr_len = 1
    trig = trig[1:]
    tss = tss[1:]
    for i, tr in enumerate(trig):
        if tr != tr_prev:
            ret_trig_values.append(tr)
            ret_trig_change_tss.append(tss[i])
            ret_trig_change_lens.append(tr_len)
            tr_prev = tr
            tr_len = 0
        tr_len += 1

    ret_trig_change_lens.append(tr_len)
            
    return ret_trig_values, ret_trig_change_tss, ret_trig_change_lens



def test():
	import doctest, sys
        sys.path.insert(1, '../../../')
        sys.path.insert(1, '../../../openbci/')
	doctest.testmod(sys.modules[__name__])
        print("Tests succeeded!")
    

#export PYTHONPATH=../../../:../../../openbci/:PYTHONPATH
if __name__ == "__main__":
   
    if TEST:
        test()
        sys.exit(0)
    
    dr = '/home/mati/bci_dev/google_openbci/openbci/temp/'
    f_name = 'test_save_timestamp'
    f = {
        'info': os.path.join(dr, f_name+'.obci.info'),
        'data': os.path.join(dr, f_name+'.obci.dat'),
        #'tags':os.path.join(dr, f_name+'.obci.tags')
       }
    if len(sys.argv) == 3:
        f = {}
        f['info'] = sys.argv[1]
        f['data'] = sys.argv[2]

    LOGGER.info("START")
    read_manager = read_manager.ReadManager(
        f['info'],
        f['data'],
        None )#f['tags'])
    vals, tss, lens = get_trigger_received_timestamps(read_manager)
    print(vals)
    print(tss)
    print(lens)
    print([x - tss[0] for x in tss])
    print([x - tss[i] for i, x in enumerate(tss[1:])])
    
        
