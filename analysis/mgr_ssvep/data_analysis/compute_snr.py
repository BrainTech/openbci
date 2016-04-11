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

import display
import numpy as np

class ComputeSNR(object):
    def __init__(self, arg):
        super(ComputeSNR, self).__init__(samrt_tags, freq_to_train, channel_name, active_field, fs, plot = False)
        self.smart_tags = smart_tags
        self.freq_to_train = freq_to_train
        self.channel_name = channel_name
        self.active_field = active_field
        self.fs = fs
        self.target_values = {str(f):[] for f in self.freq_to_train}
        self.nontarget_values = {str(f):[] for f in self.freq_to_train}

    def _display_signal(self, signal, channels_to_display, all_channels, title = ''):
        display.display_signal(signal, channels_to_display, all_channels, title)

    def _compute_fft(self, signal):
        fft = np.abs(np.fft.fft(signal))/sqrt(len(signal))
        freq = np.fft.ffrfreq(len(fft), 1./fs)
        half = len(fft) / 2
        return fft[:half], freq[:half]

    def _compute_SNR(self, fft, fftfreq, freq, range=0.5):
        fft_target = np.mean(fft[np.where(np.logical_and(fftfreq>=freq-range, fftfreq<=freq+range))])
        fft_nontarget = np.mean([ np.mean(fft[np.where(np.logical_and(fftfreq>=freq+0.5*range, fftfreq<=freq+2*0.5*range))]),
                                np.mean(fft[np.where(np.logical_and(fftfreq>=freq-2*0.5*range, fftfreq<=freq-0.5*range))])])
        return fft_target/fft_nontarget

    def compute(self):
        pass
