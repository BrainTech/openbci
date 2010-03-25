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
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

"""Run this script:
1) without parameters or with 'function' paramter to run amplifier from 
function (eg. python virtual_amplifier.py function)
2) with file info_file data_file tags_fileparameters to run amplifier 
from file 
(eg. python virtual_amplifier.py file test.obci.info test.obci.dat test.obci.tags)"""

from openbci.amplifiers import amplifiers_logging as logger
LOGGER = logger.get_logger("virtual_amplifier")

import sys
if __name__ == "__main__":
    l_mode = 'function' # default mode
    # Below, default files in case sys.argv[1] == file
    l_info_file = 'openbci/data_storage/sample_data/juhu_speller_full.obci.info'
    l_data_file = 'openbci/data_storage/sample_data/juhu_speller_full.obci.dat'
    l_tags_file = "openbci/data_storage/sample_data/juhu_speller_full.obci.tags"
    try:
        l_mode = sys.argv[1]
    except IndexError:
        pass
    if not (l_mode in ['function', 'file']):
        LOGGER.error("Unrecognised mode in first argument, \
default 'function' mode assumed.")
    
    if l_mode == 'function':
        import function_amplifier
        function_amplifier.FunctionEEGAmplifier().do_sampling()
    elif l_mode == 'file':
        try:
            l_info_file = sys.argv[2]
            l_data_file = sys.argv[3]
        except IndexError:
            LOGGER.info("No info and data files given. \
Using data_storage/sample_data/juhu_speller_full*")
        try:
            l_tags_file = sys.argv[4]
        except IndexError:
            LOGGER.info("No tags file given. \
Using data_storage/sample_data/juhu_speller_full.obci.tags")
        import file_amplifier
        file_amplifier.FileEEGAmplifier(
            {'info_file':l_info_file, 
             'data_file':l_data_file,
             'tags_file':l_tags_file
             }
            ).do_sampling()


