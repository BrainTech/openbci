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
import scipy.signal as ss
from scipy.linalg import eigh, eig

def csp_compute(smart_tags, use_channels, freq_to_train, fs):
    N = len(use_channels)
    cov_pre = np.zeros([N, N])
    cov_post = np.zeros([N, N])
    pre_i = 0
    post_i = 0

    for smart_tag in smart_tags:
        target_freq = float(smart_tag.get_tags()[0]['desc']['freq'])
        for freq in freq_to_train:
            [b, a] = ss.cheby2(1, 10, [2*(freq-1)/fs, 2*(freq+1)/fs], 'pass')
            signal_temp = np.array([ss.filtfilt(b, a, ch_samples) 
                                    for ch_samples 
                                    in smart_tag.get_channels_samples(use_channels)])
            if freq == target_freq:
                data_A = np.matrix(signal_temp)
                R_A = data_A * data_A.T / np.trace(data_A * data_A.T)
                cov_post += R_A
                post_i += 1
            else:
                data_B = np.matrix(signal_temp)
                R_B = data_B * data_B.T / np.trace(data_B * data_B.T)
                cov_pre += R_B
                pre_i += 1

    c_max = cov_post/post_i 
    c_min = cov_pre/pre_i
    vals, vects = eig(c_max, c_min+c_max)
    vals = vals.real
    vals_idx = np.argsort(vals)[::-1]
    P = np.zeros([len(vals), len(vals)])
    for i in xrange(len(vals)):
        P[:,i] = vects[:,vals_idx[i]]/np.sqrt(vals[vals_idx[i]])

    return P, vals[vals_idx]

def apply_csp_montage(signal, csp_montage,  csp_channel, all_channels_names, leave_channels=[]):
    channels_to_csp = [i for i in xrange(len(all_channels_names)) if all_channels_names[i] in csp_channel]
    print csp_channel, all_channels_names, leave_channels, signal.shape

    csp_sig = np.dot(csp_montage, signal[channels_to_csp])
    csp_sig -= csp_sig.mean()
    csp_sig /= np.sqrt(np.sum(csp_sig*csp_sig))

    if len(leave_channels):
        new_sig = np.zeros((len(leave_channels)+1, csp_sig.shape[0]))
        new_sig[0] = csp_sig
        channels_to_leave = [i for i in xrange(len(all_channels_names)) if all_channels_names[i] in leave_channels]
        print 
        new_sig[1:] = signal[channels_to_leave]
        return new_sig, 'csp_sig'

    else:
        return csp_sig, 'csp_sig'