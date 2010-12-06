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

import time
import random
import serial
import logging
import sys
import os
import getopt
import serial_test

def start_trigger_sending(port_name,num_of_trigs, min_time, max_time, send_tags, finish_saving, file_path):
    print("Start sending triggers with config:")
    print("port_name / num_of_trigs / min_time / max_time / send_tags")
    print(port_name,' / ', num_of_trigs,' / ', min_time,' / ', max_time, ' / ', send_tags)
    print("")
    secs = 20
    print("First, send 1 trigger for "+str(secs)+" secs. Then start generating other.")
    
    if file_path:
        f = open(file_path, 'w')

    if send_tags:
        from openbci.tags import tagger
        tg = tagger.get_tagger()

    s = serial_test.SerialSender(port_name)
    s.open()


    last_v = 1
    s.send(last_v)
    last_t = time.time()
    time.sleep(secs)

    for i in range(num_of_trigs):
        v = (last_v + 1) % 2
        s.send(v)
        t = time.time()
        if send_tags:
            tg.send_tag(last_t, t, "trigger", {'value': last_v})
        if file_path:
            print("write file!")
            f.write(' '.join([repr(last_t), repr(t), repr(last_v), '\n']))
            f.flush()
        last_v = v
        last_t = t
        time.sleep(min_time + random.random()*(max_time - min_time))

    # Send last tag - from last change to end-of-file
    t = time.time()
    if send_tags:
        tg.send_tag(last_t, t, "trigger", {'value': last_v})
    if file_path:
        print("write file!")
        f.write(' '.join([repr(last_t), repr(t), repr(last_v), '\n']))

    if finish_saving:
        from data_storage import signal_saver_control
        signal_saver_control.SignalSaverControl().finish_saving()

    if file_path:
        f.close()


def print_help():
    print("\nSome option is missing or is invalid. Proper use is:\n \
python auto_serial_test.py -p port_name -n num_of_trigs -s v1 -b v2 -t send_tags -f finish_saving -l file_path \n \
For example:\n \
python auto_serial_test.py -p /dev/ttyUSB0 -n 50 -s 2.2 -b 5.0 -t yes -f yes -l /a/b/f.trigger \n \n \
Where: \n \
port_name - is a path to serial port (string)\n \
num_of_trigs - is number of trigger changes to be send to serial port (int) \n \
v1 - is minimum time (in secs) for break between two trigger changes (float)\n \
v2 - is maximum time (in secs) for break between two trigger changes (float) \n \
send_tags - must be in ['yes', 'no'], determines if tags should be send to mx. \n \
finish_saving - must be in ['yes', 'no'], determines if at the end we should send finis_saving request to mx. \n \
file_path - optional - a path to file where values should be stored."
)


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "p:n:s:b:t:f:l:")
                                   
    except getopt.GetoptError, err:
        print str(err) 
        print_help()
        sys.exit(2)
    else:
        for o in ['-p', '-n', '-s', '-b','-t', '-f']:
            if not o in [opt[0] for opt in opts]:
                print("Some option is missing.")
                print_help()
                sys.exit(2)

    file_path = None
    try:
        for opt, arg in opts:
            if opt == '-p':
                port_name = arg
            elif opt == '-n':
                num_of_trigs = int(arg)
            elif opt == '-s':
                min_time = float(arg)
            elif opt == '-b':
                max_time = float(arg)
            elif opt == '-t':
                if arg == 'yes':
                    send_tags = True
                elif arg == 'no':
                    send_tags = False
                else:
                    raise Exception("-t should be in ['yes', 'no']")
            elif opt == '-f':
                if arg == 'yes':
                    finish_saving = True
                elif arg == 'no':
                    finish_saving = False
                else:
                    raise Exception("-f should be in ['yes', 'no']")
            elif opt == '-l':
                file_path = arg

    except:
        print("Some option is invalid.")
        print_help()
        sys.exit(2)

    start_trigger_sending(port_name, num_of_trigs, min_time, max_time, send_tags, finish_saving, file_path)



