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

"""Test signal saver, with this script you can send start/stop messages to signal saver."""
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
from openbci.data_storage import signal_saver_control
import sys
if __name__ == "__main__":
    l_saver_control = signal_saver_control.SignalSaverControl()
    l_path = ""
    l_session_name = ""
    l_action = ""
    try:
        l_path = sys.argv[3]
    except IndexError:
        pass
    try: 
        l_session_name = sys.argv[2]
    except IndexError:
        pass
    try:
        l_action = sys.argv[1]
    except IndexError:
        pass



    while True:
        if l_action == "finish_saving":
            l_saver_control.finish_saving()
            print("Saving to file finished. File path and nama are defined in hashtable now")
        elif l_action == "start_saving":
            l_str = "Saving to file has started. "
            if l_path == "":
                l_str = l_str + "Path is taken from Hashtable."
            else:
                l_str = l_str + "With path: " + l_path
            if l_session_name == "":
                l_str = l_str + "File name is taken from Hashtable."
            else:
                l_str = l_str + "File name: " + l_session_name
            l_saver_control.start_saving(l_session_name, l_path)
            print(l_str)
        elif l_action == "fake_finish_saving":
            l_saver_control.fake_finish_saving()


        print("Run this program with multiplexer alredy running and signal_saver.py connected.")
        print("Type:")
        print("python test_manually_signal_saver_control.py finish_saving - to finis saving to file")
        print("python test_manually_signal_saver_control.py start_saving - to start saving to file with name and path defined in Hashtable")
        print("python test_manually_signal_saver_control.py start_saving file_name file_path- to start saving to file with give name and path")

        l_action = raw_input()

