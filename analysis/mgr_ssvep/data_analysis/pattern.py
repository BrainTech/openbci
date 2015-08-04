# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#     Anna Chabuda <anna.chabuda@gmail.com>
#
import display 
import sys 

import obci.analysis.mgr_ssvep.signal_processing.pattern_analysis as SPPA


class Pattern(object):
    """docstring for Pattern"""
    def __init__(self, smart_tags, l_pattern, channel, diodas_channels, fs, l_buffer=0, 
                 number=0, display_flag=False):

        super(Pattern, self).__init__()
        self.smart_tags = smart_tags
        self.display_flag = display_flag
        self.fs = fs
        if l_buffer:
            self.pattern_type = 'l_buffer'
            self.l_buffer = l_buffer
        elif number:
            self.pattern_type = 'number'

            self.number = number
        else:
            raise "Wrong pattern_type"

        self.diodas_channels = diodas_channels
        self.channel = channel

        self.l_pattern = l_pattern

    def append_smart_tags(self, smart_tags, dioda_channel):
        self.smart_tags.append(smart_tags)
        self.diodas_channels.append(dioda_channel)

    def set_freq(self, freq):
        self.freq = freq

    def get_freq(self):
    	return self.freq

    def _display_signal(self, mgr, channels_to_display, title = ''):
        display.display_signal(mgr, channels_to_display, title)

    def _calculate_pattern_number(self, smart_tags, number, channel, dioda_channel, l_pattern, fs):
        dioda_signal, signal = SPPA.prepere_signal_to_pattern_calculate(smart_tags, channel, 
                                                                      dioda_channel)

        l_pattern_samples = int(l_pattern*fs)
        return SPPA.get_pattern_number(dioda_signal, signal, number, l_pattern_samples)

    def _calculate_pattern_buffer(self, smart_tags, l_buffer, dioda_channel, channel, l_pattern, fs):
        dioda_signal, signal = SPPA.prepere_signal_to_pattern_calculate([smart_tags], channel, 
                                                                        dioda_channel)

        l_pattern_samples = int(l_pattern*fs)
        return SPPA.get_pattern_buffer(dioda_signal, signal, l_pattern_samples)

    def calculate(self):
        if self.display_flag:
            self._display_signal(self.smart_tags[0], 
                                 self.smart_tags[0].get_param('channels_names'),
                                  'pattern_one_signal_part_0 found_blinks') 

        if self.pattern_type == 'l_buffer':
            self.pattern = [self._calculate_pattern_buffer(self.smart_tags[i], self.l_buffer, self.diodas_channels[i], self.channel, self.l_pattern, self.fs) for i in xrange(len(self.smart_tags))]

        elif self.pattern_type == "number":
            self.pattern = self._calculate_pattern_number(self.smart_tags, 
                                                          self.number, 
                                                          self.channel, 
                                                          self.diodas_channels, 
                                                          self.l_pattern, 
                                                          self.fs)



    	
        

