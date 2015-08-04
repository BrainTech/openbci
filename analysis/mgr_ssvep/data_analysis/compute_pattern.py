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

import ast

from pattern import Pattern 
import display
import obci.analysis.mgr_ssvep.signal_processing.parse_signal as SPPS
import obci.analysis.mgr_ssvep.signal_processing.parse_diode_signal as SPPDS


NUMBER = 250

MAP_DIODAS_CHANNELS = [4,5,6,7,0,1,2,3]

class ComputePattern(object):
    """docstring for ComputePattern"""
    def __init__(self, mgr, freq_to_train, l_pattern, l_train, 
                 l_buffer, offset, tag_name, channel, diodes_channels, 
                 field, display_flag=False, type_pattern='number',
                 all_field=False):

        super(ComputePattern, self).__init__()
        self.mgr = mgr
        self.fs = float(self.mgr.get_param('sampling_frequency'))
        self.freq_to_train = freq_to_train
        self.l_pattern = l_pattern
        self.l_train = l_train
        self.l_buffer = l_buffer
        self.offset = offset
        self.tag_name = tag_name
        self.diodes_channels = diodes_channels
        self.display_flag = display_flag
        self.field = field
        self.channel = channel
        self.type_pattern = type_pattern
        self.all_field = all_field

    def _display_signal(self, mgr, channels_to_display, title = ''):
        display.display_signal(mgr, channels_to_display, title)

    def _normalize_signal(self, mgr, diodes_channels):
        return SPPDS.normalize_signal(mgr, diodes_channels)

    def _found_blinks(self, mgr, diodes_channels):
        return SPPDS.found_blinks(mgr, diodes_channels)

    def _get_patterns(self, smart_tags, freq_to_train, l_pattern, 
                      diodas_channels, channel, fs, type_pattern, 
                      active_field, all_field, number='', 
                      l_buffer=''):

        patterns = {}
        smart_tags_freq = {str(freq):[] for freq in freq_to_train}
        for smart_tag in smart_tags:
            freq = smart_tag.get_tags()[0]['desc']['freq']
            smart_tags_freq[freq].append(smart_tag)

        for freq in freq_to_train:
            if type_pattern == 'number':
                patterns[str(freq)] = Pattern(smart_tags_freq[str(freq)], 
                                              l_pattern, 
                                              channel,
                                              diodas_channels[active_field],
                                              fs, 
                                              number=number)

            elif type_pattern == 'buffer':
                patterns[str(freq)] = Pattern(smart_tags_freq[str(freq)], 
                                              l_pattern, 
                                              channel,
                                              [diodas_channels[active_field]]*len(smart_tags_freq[str(freq)]),
                                              fs, 
                                              l_buffer=l_buffer)


            
            patterns[str(freq)].set_freq(freq)
            patterns[str(freq)].calculate()

        if all_field:
              patterns_nontarget = {}
              for smart_tag in smart_tags:
                  freq = smart_tag.get_tags()[0]['desc']['freq']
                  freqs = smart_tag.get_tags()[0]['desc']['freqs']
                  for ind, freq_ in enumerate(ast.literal_eval(freqs)):
                      if not freq_ == freq:
                          try:
                              patterns_nontarget['{}_non'.format(freq)].append_smart_tags(smart_tag, diodas_channels[MAP_DIODAS_CHANNELS[ind]])
                          except:
                              patterns_nontarget['{}_non'.format(freq)] = Pattern([smart_tag], 
                                                                                  l_pattern, 
                                                                                  channel,
                                                                                  [diodas_channels[MAP_DIODAS_CHANNELS[ind]]],
                                                                                  fs, 
                                                                                  l_buffer=l_buffer)
                              patterns_nontarget['{}_non'.format(freq)].set_freq(freq)
              for key in patterns_nontarget.keys():
                  patterns_nontarget[key].calculate()
              return dict(patterns.items()+patterns_nontarget.items())
        return patterns

    def calculate(self, smart_tags):
        #1. get segmentation data
        self.smart_tags = smart_tags

        if self.display_flag:
            self._display_signal(self.smart_tags[0], 
                                 self.smart_tags[0].get_param('channels_names'),
                                  'pattern_signal_part_0')
            
        #2. normalize diodes signal
        for ind in range(len(self.smart_tags)):
            self.smart_tags[ind] = self._normalize_signal(self.smart_tags[ind], 
                                                          self.diodes_channels)
        if self.display_flag:
            self._display_signal(self.smart_tags[0], 
                                 self.smart_tags[0].get_param('channels_names'),
                                  'pattern_signal_part_0 diode normalize')
        #3. found blinks found 
        for ind in range(len(self.smart_tags)):
            self.smart_tags[ind] = self._found_blinks(self.smart_tags[ind], 
                                                          self.diodes_channels)
        if self.display_flag:
            self._display_signal(self.smart_tags[0], 
                                 self.smart_tags[0].get_param('channels_names'),
                                  'pattern_signal_part_0 found_blinks')   
        
         # 4. get pattern 
        return self._get_patterns(self.smart_tags, 
                                  self.freq_to_train, 
                                  self.l_pattern, 
                                  self.diodes_channels, 
                                  self.channel,
                                  self.fs,
                                  self.type_pattern,
                                  self.field,
                                  self.all_field, 
                                  number=NUMBER, 
                                  l_buffer=self.l_buffer)
