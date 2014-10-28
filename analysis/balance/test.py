# -*- coding: utf-8 -*-
from __future__ import print_function, division
from wii_preprocessing import *
from wii_analysis import *
import matplotlib.pyplot as py

if __name__ == '__main__':
	w = WBBReadManager('test1.obci.xml','test1.obci.raw','test1.obci.tag')
	w.get_x()
	w.get_y()
	wbb_mgr = wii_filter_signal(w, 30.0, 2, use_filtfilt=False)
	wbb_mgr = wii_downsample_signal(wbb_mgr, factor=4, pre_filter=False, use_filtfilt=False)
	smart_tags = wii_cut_fragments(wbb_mgr)
	for sm in smart_tags:
		sm_x = sm.get_channel_samples('x')
		sm_y = sm.get_channel_samples('y')
		py.figure()
		print(wii_COP_path(wbb_mgr, sm_x, sm_y, plot=True))
	py.show()