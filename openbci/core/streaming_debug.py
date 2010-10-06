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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>

"""
Use to debug real-life streaming modules like:
- amplifier
- streamer
- filter
See signal_streamer_no_filter.py for sample use.
"""
import time
class Debug(object):
    def __init__(self, p_sampling, logger):
        """By now init externally given logger 
        (python standar logger object) and sampling."""
        self.num_of_samples = 0
        self.sampling = p_sampling
        self.logger = logger
        self.start_time = time.time()
        self.last_pack_time = self.start_time

    def next_sample(self):
        """Called after every new sample received.
        Aftet sel.sampling sample print stats info."""
        self.num_of_samples += 1
        if self.num_of_samples % self.sampling == 0:
            self.logger.info(''.join(
                    ["Time of last ",
                     str(self.sampling),
                     " samples / all avg: ",
                     str(time.time() - self.last_pack_time),
                     ' / ', 
                     str(self.sampling*(time.time() - self.start_time)/float(self.num_of_samples))]))
            self.last_pack_time = time.time()
