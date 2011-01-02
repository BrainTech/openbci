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
#
import logic_speller_engine
import logic_speller_server
import settings

import sys, os.path
import settings
if __name__ == "__main__":
    l_config = 'speller_config' # default mode
    try:
        l_config = sys.argv[1]
    except IndexError:
        pass
    l_server = logic_speller_server.LogicSpellerServer(settings.MULTIPLEXER_ADDRESSES)
    l_engine = logic_speller_engine.LogicSpellerEngine(l_server, l_config)
    l_server.set_engine(l_engine)
    l_server.loop()

 
