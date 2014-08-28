# -*- coding: utf-8 -*-
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as py
from obci.analysis.obci_signal_processing import read_manager
from obci.analysis.obci_signal_processing.signal import read_data_source
from obci.analysis.obci_signal_processing.tags import smart_tag_definition
from obci.analysis.obci_signal_processing import smart_tags_manager
import copy
import scipy.signal as ss
from raw_preprocessing import *
from wii_read_manager import *

def wii_downsample_signal(wbb_mgr, factor=2, pre_filter=False, use_filtfilt=False):
	""" Returns WBBReadManager object with downsampled signal values 
	Input:
	wbb_mgr 			-- WBBReadManager object
	factor 				-- int 	-- downsample signal to sampling rate original_sampling_frequency / factor 
	pre_filter 			-- bool -- use lowpass filter with cutoff frequency sampling_frequency / 2
	use_filtfilt 		-- bool -- use filtfilt in filtering procedure (default lfilter)
	"""

	if pre_filter:
		fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
		wbb_mgr = wii_filter_signal(wbb_mgr, fs/2, 4, use_filtfilt)
		samples = wbb_mgr.mgr.get_samples()
	else:
		samples = wbb_mgr.mgr.get_samples()

	new_samples = raw_downsample_signal(samples, factor)

	info_source = copy.deepcopy(wbb_mgr.mgr.info_source)
	info_source.get_params()['number_of_samples'] = str(len(new_samples[0]))
	info_source.get_params()['sampling_frequency'] = str(float(wbb_mgr.mgr.get_param('sampling_frequency'))/factor)
	tags_source = copy.deepcopy(wbb_mgr.mgr.tags_source)
	samples_source = read_data_source.MemoryDataSource(new_samples)
	return WBBReadManager(info_source, samples_source, tags_source)

def wii_filter_signal(wbb_mgr, cutoff_upper, order, use_filtfilt=False):
	""" Returns WBBReadManager object with filtered signal values 
	Input:
	wbb_mgr 			-- WBBReadManager object
	cutoff_upper 		-- float -- cutoff frequency
	order 				-- int   -- order of filter
	use_filtfilt 		-- bool -- use filtfilt in filtering procedure (default lfilter)
	"""

	fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
	samples = wbb_mgr.mgr.get_samples()
	new_samples = raw_filter_signal(samples, fs, cutoff_upper, order, use_filtfilt)

	info_source = copy.deepcopy(wbb_mgr.mgr.info_source)
	tags_source = copy.deepcopy(wbb_mgr.mgr.tags_source)
	samples_source = read_data_source.MemoryDataSource(new_samples)
	return WBBReadManager(info_source, samples_source, tags_source)

def wii_fix_sampling(wbb_mgr):

	return

def wii_cut_fragments(wbb_mgr):
	""" Returns SmartTags object with cut signal fragments according to 'start' - 'stop' tags
	"""

	x = smart_tag_definition.SmartTagEndTagDefinition(start_tag_name='start', 
													  end_tags_names=['stop'])
	smart_mgr = smart_tags_manager.SmartTagsManager(x, None, None, None, wbb_mgr.mgr)
	return smart_mgr.get_smart_tags()