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
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import variables_pb2

import data_storage_logging as logger
LOGGER = logger.get_logger("signal_saver_control")


class SignalSaverControl(object):
    """An instance of the class provides a convinient interface for
    starting and finishig saving signal to file. Use it as API for that 
    purpose."""
    def __init__(self):
        """Init connection."""
        self._connection = connect_client(type = peers.SIGNAL_SAVER_CONTROL)
    def start_saving(self, p_file_name="", p_file_path=""):
        """Send start_saving message to signal_saver. If p_file_path, 
        p_file_name are giver, set those variables in hashtable before,
        so that signal_saver saves signal to that destination."""
        l_var = variables_pb2.Variable()
        if p_file_name != "":
            l_var.key = "SaveFileName"
            l_var.value = p_file_name
            self._connection.send_message(message = l_var.SerializeToString(), 
                                         type = types.DICT_SET_MESSAGE, 
                                         flush=True)
            LOGGER.info("Set hashtable.SaveFileName to: "+p_file_name)
        if p_file_path != "":
            l_var.key = "SaveFilePath"
            l_var.value = p_file_path
            self._connection.send_message(message = l_var.SerializeToString(), 
                                         type = types.DICT_SET_MESSAGE, 
                                         flush=True)
            LOGGER.info("Set hashtable.SaveFilePath to: "+p_file_path)

        #self._send_message("start_saving")
            
    def finish_saving(self):
        """Send finish_saving message to signal saver."""
        self._send_message("finish_saving")

    def fake_finish_saving(self):

        l_vec = variables_pb2.VariableVector()

        l_var = l_vec.variables.add()
        l_var.key = 'first_sample_timestamp'
        l_var.value = repr(1000.0)

        l_var = l_vec.variables.add()
        l_var.key = 'number_of_samples'
        l_var.value = str(9999)

        l_var = l_vec.variables.add()
        l_var.key = 'file_path'
        l_var.value = 'path'

        self._connection.send_message(
            message=l_vec.SerializeToString(), 
            type=types.SIGNAL_SAVER_CONTROL_MESSAGE, flush=True)
        
    def _send_message(self, p_msg):
        """Send p_msg message to mx with SIGNAL_SAVER_FINISH_SAVING type."""
        LOGGER.info("Send "+p_msg)
        l_msg_type = types.SIGNAL_SAVER_FINISH_SAVING
        self._connection.send_message(message=p_msg,
                                      type=l_msg_type, flush=True)

if __name__ == '__main__':
    l_saver_control = SignalSaverControl()
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

    else:
        print ("No action pefromed.")
