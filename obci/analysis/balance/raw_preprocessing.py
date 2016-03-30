# -*- coding: utf-8 -*-
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as py
import scipy.signal as ss

def raw_downsample_signal(signal, factor):
	""" Returns downsampled signal values (according to factor) """ 
	ch_num = len(signal)
	ch_len = len(signal[0])
	ret_sig_len = 0
	i = 0
	left_inds = []
	while i < ch_len:
		left_inds.append(i)
		ret_sig_len += 1
		i += factor
	new_samples = np.array([np.zeros(ret_sig_len) for i in range(ch_num)])
	for i in range(ch_num):
		for j, ind in enumerate(left_inds):
			new_samples[i,j] = signal[i,ind]
	return new_samples

def raw_filter_signal(signal, fs, cutoff_upper, order, use_filtfilt=False):
	""" Returns signal values filtered with Butterworth lowpass filter """

	[a,b] = ss.butter(order, cutoff_upper/fs, btype='lowpass')
	if use_filtfilt:
		new_signal = np.array([ss.filtfilt(a, b, s) for s in signal])
	else:
		new_signal = np.array([ss.lfilter(a, b, s) for s in signal])
	return new_signal

def raw_fix_sampling(signal):
	""" Returns raw signal values with fixed sampling rate """

	return

