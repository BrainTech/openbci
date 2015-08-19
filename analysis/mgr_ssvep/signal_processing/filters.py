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


import scipy.signal as ss
import numpy as np

def highpass_filter(signal, channels_to_filt, all_channels, fs):
    #cuttoff mena sig 
    [a,b] = ss.butter(2, 5/(fs/2), btype='high')
    for ind, (ch_samples, ch_name) in enumerate(zip(signal, 
                                                    all_channels)):
        if ch_name in channels_to_filt:
            signal[ind] -= np.mean(ch_samples)

    return signal

def cheby2_bandpass_filter(signal, channels_to_filt, all_channels, fs):
    [a,b] = ss.cheby2(3, 50,[49/(fs/2),51/(fs/2)], btype='bandstop', analog=0)
    for ind, (ch_samples, ch_name) in enumerate(zip(signal, 
                                                    all_channels)):
        if ch_name in channels_to_filt:
            # filtered_signal[ind] = ss.filtfilt(a, b, ch_samples)
            tmp = np.r_[ch_samples[::-1][0:-1], ch_samples, ch_samples[::-1][1:]]
            # import matplotlib.pyplot as plt 
            # plt.plot(tmp)
            signal[ind] = ss.filtfilt(a, b, tmp)[ch_samples[0:-1].shape[0]:-ch_samples[1:].shape[0]] 
            # plt.plot(signal[ind])
            # plt.show()
     # print filtered_signal.shape
        # return 'd'
    return signal[:,0.2*512+45:-0.2*512]