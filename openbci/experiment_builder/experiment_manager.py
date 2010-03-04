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

# FIXME: Temporarily we create config here, and not from files
CONFIG = {}
CONFIG['screens'] = [['lipne/zolty', 'lipne/czerwony'], ['lipne/bialy', 'lipne/czarny'], ['lipne/niebieski', 'lipne/zielony']]
CONFIG['delay'] = 10

from ugm.ugm_config_manager import UgmConfigManager
import random
import time

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
        
    def run(self):
        for i_screens_pack in self.screens:
            random.shuffle(i_screens_pack)
        random.shuffle(self.screens)
        
        for i_screens_pack in self.screens:
            print('pack')
            for i_screen in i_screens_pack:
                print('screen')
                l_tempConfigManager = UgmConfigManager()
                l_tempConfigManager.update_from_file(i_screen, True)
                l_tempConfigManager.update_to_file('ugm_config', True)
                time.sleep(10)
                self._post_screen()
            self._post_screen_package()
        
    def _post_screen_package(self):
        print('\a')
        
    def _post_screen(self):
        print('\a')

def main():
    l_experiment_manager = Experiment_manager()
    l_experiment_manager.run()

if __name__ == '__main__':
    main()