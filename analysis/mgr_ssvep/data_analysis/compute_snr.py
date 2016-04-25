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
import ast

class ComputeSNR(object):
    def __init__(self, smart_tags, freq_to_train, channel_name, active_field, fs, target, nontarget, plot = False):
        super(ComputeSNR, self).__init__()
        self.smart_tags = smart_tags
        self.freq_to_train = freq_to_train
        self.channel_name = channel_name
        self.active_field = active_field
        self.fs = fs
        self.target = target
        self.nontarget = nontarget

    def _display_signal(self, signal, channels_to_display, all_channels, title = ''):
        display.display_signal(signal, channels_to_display, all_channels, title)

    def _compute_fft(self, signal):
        fft = np.abs(np.fft.fft(np.blackman(len(signal))*signal, 10*512))/np.sqrt(len(signal))
        freq = np.fft.fftfreq(len(fft), 1./self.fs)
        half = len(fft) / 2
        return fft[:half], freq[:half]

    def _compute_SNR(self, fft, fftfreq, freq, range=0.3, offset=0.6):
        # print ">=freq-range", freq-range, "<=freq+range", freq+range
        # print 'target', fftfreq[np.where(np.logical_and(fftfreq>=freq-range, fftfreq<=freq+range))]
        fft_target = np.mean(fft[np.where(np.logical_and(fftfreq>=freq-range, fftfreq<=freq+range))])
        # print fft_target
        # print '>=', freq+range, ' <=', freq+2*range
        # print 'nontarget', fftfreq[np.where(np.logical_and(fftfreq>freq+offset, fftfreq<=freq+offset+ range))]
        # print '>=', freq-2*range, ' <=', freq-range
        # print 'nontarget', fftfreq[np.where(np.logical_and(fftfreq>=freq-range-offset, fftfreq<freq-offset))]
        fft_nontarget = np.mean([ np.mean(fft[np.where(np.logical_and(fftfreq>freq+offset, fftfreq<=freq+offset+ range))]),
                                np.mean(fft[np.where(np.logical_and(fftfreq>=freq-range-offset, fftfreq<freq-offset))])])
        # print fft_nontarget
        return fft_target/fft_nontarget

    def compute(self):

        for st in self.smart_tags:
            signal = st.get_channel_samples(self.channel_name)
            freq_target = st.get_tags()[0]['desc']['freq']
            freq_nontarget = ast.literal_eval(st.get_tags()[0]['desc']['freqs'])
            freq_nontarget.remove(freq_target)
            try:
                freq_nontarget.remove(str(int(freq_target)+1))
            except:
                pass
            try:
                freq_nontarget.remove(str(int(freq_target)-1))
            except:
                pass

            fft, freq = self._compute_fft(signal)
            snr_value = self._compute_SNR(fft, freq, int(freq_target), range=0.3)
            self.target[freq_target].append(snr_value)
            # import matplotlib.pyplot as plt
            # print freq_target
            # plt.stem(freq,fft)
            # plt.show()
            for i in freq_nontarget:
                snr_value = self._compute_SNR(fft, freq, int(i), range=0.3)
                self.nontarget[i].append(snr_value)
        return self.target, self.nontarget


