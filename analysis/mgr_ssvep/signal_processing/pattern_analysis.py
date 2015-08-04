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

import numpy as np

def prepere_signal_to_pattern_calculate(smart_tags, channel, dioda_channel):
    signal = np.array([])
    dioda_signal = np.array([])
    for smart_tag in smart_tags:
        dioda_syg = smart_tag.get_channel_samples(dioda_channel)
        channel_syg = smart_tag.get_channel_samples(channel)
        stimulus_starts_ind = np.where(dioda_syg >= 1)[0]
        signal = np.concatenate((signal, channel_syg[int(stimulus_starts_ind[0]):int(stimulus_starts_ind[-1])]), axis=0)
        dioda_signal = np.concatenate((dioda_signal, dioda_syg[stimulus_starts_ind[0]:stimulus_starts_ind[-1]]), axis=0)
    return dioda_signal, signal

def get_pattern_number(dioda_signal, signal, number, l_pattern_samples):
    blinks = np.where(dioda_signal == 1)[0]
    preper_signal = np.r_[signal, signal]

    if number > len(blinks):
        print "Number > blinks, get pattern from {} blinks".format(len(blinks))
        number = len(blinks)

    pattern = np.mean(np.array([preper_signal[i:i+l_pattern_samples] for i in blinks[:number]]), axis=0)
    return pattern

def get_pattern_buffer(dioda_signal, signal, l_pattern_samples):
    blinks = np.where(dioda_signal == 1)[0]
    preper_signal = np.r_[signal, signal]
    pattern = np.mean(np.array([preper_signal[i:i+l_pattern_samples] for i in blinks]), axis=0)
    return pattern