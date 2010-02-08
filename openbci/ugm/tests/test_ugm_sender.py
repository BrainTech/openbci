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

"""Run this module as a script to send update messages to ugm.
The script should be fired when multiplexer is alredy up."""
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import  connect_client
from ugm import ugm_config_manager
class TestUgmSender(object):
    """Fire run() to send update messages to ugm.
    The method should be fired when multiplexer is alredy up."""
    def __init__(self):
        """Init connection to be used to send UGM_UPDATE_MESSAGES."""
        self._connection = connect_client(type = peers.LOGIC)
    def run(self):
        """Send ugm.configs.test1 config to ugm and then wait in a loop
        for config proposed by the user - then send to ugm config
        from prompt."""
        l_mgr = ugm_config_manager.UgmConfigManager()
        i = 0
        while True:
            i = i + 1
            print("Type: 0 ugm.configs.some_config to rebuild ugm from some_config.py")
            print("Type 1 ugm.configs.some_config to update config for ugm from some_config.py")
            if i > 1:
                l_input = raw_input()
            else:
                l_input = '0 ugm.configs.test1'
            l_type, l_config = l_input.split(" ")
            l_msg = variables_pb2.UgmUpdate()
            l_msg.type = int(l_type)
            # Let config manager read data from config file
            l_mgr.update_from_file(l_config)
            # Data is red...
            # Let`s convert red data to message ready to be sent
            l_msg.value = l_mgr.config_to_message()
            self._connection.send_message(
                message = l_msg.SerializeToString(), 
                type=types.UGM_UPDATE_MESSAGE, flush=True)
if __name__ == "__main__":
    TestUgmSender().run()
 
