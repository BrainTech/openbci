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

from offline_analysis import offline_analysis_logging as logger
LOGGER = logger.get_logger("trigger")

def fix_trigger(trig_values, trig_change_tss, trig_change_lens, min_trig_samples_len=0):
    """
    For given trigger parameters (described in output description of get_trigger)
    try to remove very short triggers (of samples length - min_trig_samples_len)
    as this is considered as an unexpected fluctuation, not planned trigger.

    >>> fix_trigger([1,0,1,0,1,0], [1,2,3,4,5,6], [20, 5, 30, 6, 5, 4], 6)
    ([1, 0], [1, 4], [55, 15])

    >>> fix_trigger([1], [100], [20000], 6)
    ([1], [100], [20000])

    >>> fix_trigger([1], [100], [20000], 20001)
    ([], [], [])

    >>> fix_trigger([1], [100], [20000], 20000)
    ([1], [100], [20000])

    >>> fix_trigger([1,0,1,0], [10,20,30,40], [5, 100, 150, 200], 6)
    ([0, 1, 0], [20, 30, 40], [100, 150, 200])

    >>> fix_trigger([1,0,1,0], [10,20,30,40], [5, 10, 15, 20], 16)
    ([0], [40], [20])

    >>> fix_trigger([1,0,1,0,1], [10,20,30,40,50], [20, 5, 10, 15, 20], 16)
    ([1], [10], [70])
    
    """
    LOGGER.info("Fix trigger fired...")

    # Cope with specific situations...
    if  len(trig_change_lens) == 0:
        return [], [], []
    elif len(trig_change_lens) == 1:
        if trig_change_lens[0] < min_trig_samples_len:
            return [], [], []
        else:
            return trig_values, trig_change_tss, trig_change_lens


    # Init values to-be-returned
    ret_trig_change_tss = []
    ret_trig_values = []
    ret_trig_change_lens = []

    i = 0

    # If true, fire fix_trigger once more - it migh happen, that we remove fluctuation
    # but still it all looks as fluctuation and must be checked, eg:
    # we have [1,1,1,1,0,0,0,0,1,0,1,0,0,0,0] and min_trig_samples_len == 4
    # below procedure will create sth like:
    # [1,1,1,1,0,0,0,0,1,1,1,0,0,0,0] and this is not what we want, fix_trigger must
    # be called again, so that we get:
    # [1,1,1,1,0,0,0,0,0,0,0,0,0,0,0]
    short_found = False
    while i < len(trig_change_lens):
        if trig_change_lens[i] >= min_trig_samples_len:
            # If trigger length is enough
            ret_trig_change_lens.append(trig_change_lens[i])
            ret_trig_values.append(trig_values[i])
            ret_trig_change_tss.append(trig_change_tss[i])
            i += 1
        else:
            # At least one trigger was too short
            short_found = True

            if len(ret_trig_change_lens) == 0:
                # If this is the first trigger, just ignore it
                # as it was never there
                i += 1
            elif i == len(trig_change_lens) - 1:
                # If this is the last trigger, append its len. to previous trigger
                ret_trig_change_lens[-1] += trig_change_lens[i]                
                i += 2
            else:
                # if this trigger is somewere 'inside'
                # merge this trigger with its predecessor and successor
                ret_trig_change_lens[-1] += trig_change_lens[i] + trig_change_lens[i+1]
                i += 2

    if short_found:
        LOGGER.info("Go deeper in fix_trigger...")
        return fix_trigger(ret_trig_values, ret_trig_change_tss, ret_trig_change_lens, min_trig_samples_len)
    else:
        return ret_trig_values, ret_trig_change_tss, ret_trig_change_lens


def get_trigger(p_read_mgr, min_trig_len=0.0, trig=None, sampling=None):
    """
    >>> get_trigger(None, 0.0, [1,0,0,0,1,1,1,0,1,1,1], 128.0)
    ([1, 0, 1, 0, 1], [0.0, 0.0078125, 0.03125, 0.0546875, 0.0625], [1, 3, 3, 1, 3])

    >>> get_trigger(None, 0.1, [1,0,0,0,1,1,1,1,0,0,1,1,1,1,1], 128.0)
    ([], [], [])

    >>> get_trigger(None, 0.02, [1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1], 128.0)
    ([0, 1], [0.015625, 0.0390625], [3, 11])

    >>> get_trigger(None, 0.02, [1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1], 128.0)
    ([1, 0, 1], [0.0, 0.0234375, 0.046875], [3, 3, 11])

    """
    #tss = p_read_mgr.get_channel_values("TIMESTAMPS")

    if p_read_mgr:
        trig = p_read_mgr.get_channel_samples("TRIGGER")
        sampling = float(p_read_mgr.get_param('sampling_frequency'))
    else:
        # Assumint trig and sampling != None
        pass

    #Determine samples timestamps assuming first sample`s ts is 0
    tss = [i/sampling for i in range(len(trig))]
    LOGGER.info("Trigger channel length: "+str(len(trig)))

    # Compute results...
    ret_trig_change_tss = [tss[0]]
    ret_trig_values = [trig[0]]
    ret_trig_change_lens = []

    # Previous trigger value
    tr_prev = trig[0]

    # Current trigger length (in samples)
    tr_len = 1
    l_trig = trig[1:]
    l_tss = tss[1:]
    for i, tr in enumerate(l_trig):
        if tr != tr_prev:
            ret_trig_values.append(tr)
            ret_trig_change_tss.append(l_tss[i])
            ret_trig_change_lens.append(tr_len)
            tr_prev = tr
            tr_len = 0
        tr_len += 1

    ret_trig_change_lens.append(tr_len)
    #LOGGER.info("LEN LEN "+str(len(ret_trig_values))+" / "+str(len(ret_trig_change_tss))+" / "+str(len(ret_trig_change_lens)))
    #LOGGER.info(str(ret_trig_values))
    #LOGGER.info(str(ret_trig_change_tss))
    #LOGGER.info(str(ret_trig_change_lens))
    #LOGGER.info("min trig len: "+str(min_trig_len*sampling))

    return fix_trigger(ret_trig_values, ret_trig_change_tss, ret_trig_change_lens, min_trig_len*sampling)

def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")


if __name__ == "__main__":
    test()
    
