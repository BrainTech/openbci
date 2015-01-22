#!/usr/bin/env python
# -*- coding: utf-8 -*-

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import wii_confidence_ellipse_area as get_ellipse_area
from obci.analysis.balance.wii_preprocessing import *

from obci.acquisition import acquisition_helper

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


def show_results(x, y, xa, ya, xb, yb, xc, yc):
    plt.figure()
    ax = plt.gca()
    plt.plot(x, y)
    ellipse = Ellipse(xy=(xc, yc), width=xa, height=yb, edgecolor='r', fc='None', lw=5,)
    ax.add_patch(ellipse)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.show()

def estymate_fs(TSS_samples):
    durations = []
    for ind in range(1, len(TSS_samples)):
        durations.append(TSS_samples[ind]-TSS_samples[ind-1])
    return 1.0/np.mean(durations)

def calculate(file_path, file_name, show=True):
    file_name = acquisition_helper.get_file_path(file_path, file_name)
    w = WBBReadManager(file_name+'.obci.xml', file_name+'.obci.raw', file_name+'.obci.tag')
    w.get_x()
    w.get_y()
    w.mgr.set_param('sampling_frequency', estymate_fs(w.mgr.get_channel_samples('TSS')))
    w = wii_filter_signal(w, 30.0, 2, use_filtfilt=False)
    w = wii_downsample_signal(w, factor=4, pre_filter=False, use_filtfilt=False)
    smart_tags = wii_cut_fragments(w, start_tag_name='ss_start', end_tags_names=['ss_stop'])
    x = smart_tags[0].get_channel_samples('x')
    y = smart_tags[0].get_channel_samples('y')
    xa, ya = np.std(x)*3, np.mean(y)
    xb, yb = np.mean(x), np.std(y)*3
    xc, yc = np.mean(x), np.mean(y)
    if show:
        show_results(x, y, xa, ya, xb, yb, xc, yc)
    return xa, ya, xb, yb, xc, yc 
