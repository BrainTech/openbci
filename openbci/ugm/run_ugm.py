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

"""Current script is supposed to be fired if you want to run 
ugm as a part of openbci (with multiplexer and all that stuff)."""

import configurer
from ugm import ugm_engine
from ugm import ugm_internal_server
from ugm import ugm_config_manager
import settings
import thread, os

if __name__ == "__main__":
    # Create instance of ugm_engine with config manager (created from
    # default config file
    configs = configurer.Configurer(settings.MULTIPLEXER_ADDRESSES).get_configs(['UGM_CONFIG', 'UGM_USE_TAGGER', 'UGM_INTERNAL_IP', 'UGM_INTERNAL_PORT'])
    ENG = ugm_engine.UgmEngine(ugm_config_manager.UgmConfigManager(configs['UGM_CONFIG']))
    thread.start_new_thread(ugm_internal_server.UdpServer(ENG, 
                                                          configs['UGM_INTERNAL_IP'],
                                                          int(configs['UGM_INTERNAL_PORT']),
                                                          int(configs['UGM_USE_TAGGER'])).run, ())

    # Start multiplexer in a separate process
    path = os.path.join(settings.module_abs_path(), "ugm_server.py")
    os.system("python " + path + " &")

    #TODO - works only when running from openbci directiory...
    # fire ugm engine in MAIN thread (current thread)
    ENG.run()


