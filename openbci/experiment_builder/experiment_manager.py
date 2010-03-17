# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#      Łukasz Polak <l.polak@gmail.com>
#
"""Holds Experiment_manager class:
This class is responsible for managing UGM experiments. It loads and holds configs
of those experiments and makes it possible to run them"""

from ugm.ugm_config_manager import UgmConfigManager
from experiment_builder.config.config import CONFIG, USE_MULTIPLEXER
import random	
import time

if USE_MULTIPLEXER:
    from multiplexer.multiplexer_constants import peers, types
    from multiplexer.clients import connect_client
    import variables_pb2

class Experiment_manager(object):
    """This class is responsible for managing UGM experiments. It loads and holds configs
    of those experiments and makes it possible to run them"""
    def __init__(self, p_config_file=None):
        super(Experiment_manager, self).__init__()
        # FIXME: Temporarily we just use some built-in values
        global CONFIG
        p_config_file = CONFIG
        self.screens = p_config_file['screens']
        self.delay = p_config_file['delay']
        self.config_manager = UgmConfigManager()
        self._connection = None
        
    def run(self):
        for i_screens_pack in self.screens:
            random.shuffle(i_screens_pack)
        random.shuffle(self.screens)
        
        time.sleep(10)
        for i_screens_pack in self.screens:
            print('pack')
            for i_screen in i_screens_pack:
                print('screen ' + i_screen)
                self.config_manager.update_from_file(i_screen, True)
                self.send_to_ugm()
                time.sleep(10)
                self._post_screen()
            self._post_screen_package()

    def send_to_ugm(self):
        if USE_MULTIPLEXER:
            l_type = 0
            l_msg = variables_pb2.UgmUpdate()
            l_msg.type = int(l_type)
            l_msg.value = self.config_manager.config_to_message()
                
            # Everything done :) All that is left is to establish connection if needed...
            if not self._connection:
                self._connection = connect_client(type = peers.LOGIC)
            # ...and send message to UGM
            self._connection.send_message(
                message = l_msg.SerializeToString(), 
                type=types.UGM_UPDATE_MESSAGE, flush=True)
        else:
            self.config_manager.update_to_file('ugm_config', True)
        
    def _post_screen_package(self):
        print('\a')
        
    def _post_screen(self):
        print('\a')

def main():
    l_experiment_manager = Experiment_manager()
    l_experiment_manager.run()

if __name__ == '__main__':
    main()
