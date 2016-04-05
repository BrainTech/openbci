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
sys.path.insert(1, '../../../')
sys.path.insert(1, '../../../openbci/')

import os.path
import math
from openbci.offline_analysis.obci_signal_processing import read_manager
import trigger_change
from core import core_logging as logger
LOGGER = logger.get_logger("trigger_analysis", "debug")

from pylab import *
def compare_send_and_received(sent_vals, sent_tss, rcv_vals, rcv_tss, f_name):
    sent_vals = sent_vals[1:]
    sent_tss = sent_tss[1:]
    rcv_vals = rcv_vals[1:]
    rcv_tss = rcv_tss[1:]
    if not sent_vals == [(x + 1) % 2 for x in rcv_vals]:
        LOGGER.error(''.join(["Values of the trigger received from amplifier are different from values sent to serial port.",
                              " Received values length: ", str(len(rcv_vals)),
                              ". Sent values length: ", str(len(sent_vals)),
                              ". Processing aborted!"]))
        sys.exit(1)

    tss_diff = [rcv_tss[i] - a for i, a in enumerate(sent_tss)]
    min_diff = min(tss_diff)
    max_diff = max(tss_diff)
    avg_diff = sum(tss_diff)/len(tss_diff)
    std_dev = math.sqrt(sum([(x-avg_diff)*(x-avg_diff) for x in tss_diff])/len(tss_diff))
    

    LOGGER.info("***************************************************************")
    LOGGER.info("STATISTICS REPORT:")
    LOGGER.info("Minimum Rcv - sent diff: "+str(min_diff))
    LOGGER.info("Maximum Rcv - sent diff: "+str(max_diff))
    LOGGER.info("Rcv - sent avg: "+str(avg_diff))
    LOGGER.info("Rcv - sent std dev: "+str(std_dev))
    LOGGER.info("***************************************************************")

    ff = open(f_name+'.txt', 'w')
    ff.write("STATISTICS REPORT:\n")
    ff.write("Minimum Rcv - sent diff: "+str(min_diff))
    ff.write('\n')
    ff.write("Maximum Rcv - sent diff: "+str(max_diff))
    ff.write('\n')
    ff.write("Rcv - sent avg: "+str(avg_diff))
    ff.write('\n')
    ff.write("Rcv - sent std dev: "+str(std_dev))
    ff.close()
    figure(0)
    plot(sent_tss)
    plot(rcv_tss)
    #legend("Sent timestamps", "Received timestmaps")
    title("Sent and received timestamps")

    figure(1)
    plot(tss_diff)
    plot([avg_diff]*len(tss_diff))
    title("Received_trigger_ts-Sent_trigger_ts")
    legend(("Rcv_ts-Sent_ts", "avg(Rcv_ts-Sent_ts)"))
    show()


if __name__ == "__main__":
    
    dr = '/home/mati/bci_dev/openbci_repo/trunk/temp/'
    f_name = 'synchro_test_02_12_2010_22ch_1024hz_c++_usb'
    f = {
        'info': os.path.join(dr, f_name+'.obci.svarog.info'),
        'data': os.path.join(dr, f_name+'.obci.dat'),
        'tags':os.path.join(dr, f_name+'.obci.svarog.tags')
       }
    read_manager = read_manager.ReadManager(
        f['info'],
        f['data'],
        f['tags'])

    asci_trig = ''#os.path.join(dr, f_name+'.asci_trigger')
    if os.path.isfile(asci_trig):
        sent_vals, sent_tss = trigger_change.get_trigger_sent_timestamps(None, asci_trig)
    else:
        sent_vals, sent_tss = trigger_change.get_trigger_sent_timestamps(read_manager, None)

    rcv_vals, rcv_tss, rcv_len = trigger_change.get_trigger_received_timestamps(read_manager)


    LOGGER.info("*******************************************")
    LOGGER.info("Red sent vals: ")
    LOGGER.info(sent_vals)
    LOGGER.info("Red sent tss: ")
    LOGGER.info(sent_tss)

    LOGGER.info("*******************************************")
    LOGGER.info("Red rcv vals: ")
    LOGGER.info(rcv_vals)
    LOGGER.info("Red rcv tss: ")
    LOGGER.info(rcv_tss)
    LOGGER.info("Red rcv lens: ")
    LOGGER.info(rcv_len)

    ff = open(f_name+'.data.txt', 'w')
    ff.write(','.join([repr(i) for i in sent_vals]))
    ff.write('\n')
    ff.write(','.join([repr(i) for i in sent_tss]))
    ff.write('\n')
    ff.write(','.join([repr(i) for i in rcv_vals]))
    ff.write('\n')
    ff.write(','.join([repr(i) for i in rcv_tss]))
    ff.write('\n')
    ff.close()

    compare_send_and_received(sent_vals, sent_tss, rcv_vals, rcv_tss, f_name)

    #print([x - tss[0] for x in tss])
    #print([x - tss[i] for i, x in enumerate(tss[1:])])
    
        
