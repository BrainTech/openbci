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

def normalize_signal(mgr, channels_names):
    for ch_name in channels_names:
        signal = mgr.get_channel_samples(ch_name)
        min_signal = signal.min()
        signal[:] -= np.ones(signal.shape)*min_signal
        max_signal = signal.max()
        signal[:] /= max_signal

    return mgr

def found_blinks(mgr, channels_names):
    for ch_name in channels_names:
        signal = mgr.get_channel_samples(ch_name)
        flag, ind = 0, 0
        blinks = np.zeros(len(signal))
        while ind < len(signal):
            if signal[ind]<0.2:
                if  flag == 0:
                    flag = 1
            if (signal[ind] > 0.8):
                if flag==1:
                    flag = 0
                    blinks[ind] = 1
            ind+=1
        signal[:] = blinks
        
    return mgr