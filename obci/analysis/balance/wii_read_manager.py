# -*- coding: utf-8 -*-

from __future__ import print_function, division
from obci.analysis.obci_signal_processing import read_manager
import numpy as np
import wii_utils

class WBBReadManager(object):

    def __init__(self, info_source, data_source, tags_source):
        super(WBBReadManager, self).__init__()

        try:
            self.mgr = read_manager.ReadManager(info_source, 
                                                data_source, 
                                                tags_source) 
        except IOError, e:
            raise Exception("\n[ERROR]\t{}".format(e))

    def get_raw_signal(self):
        """ Returns raw sensor data (TopRight, TopLeft, BottomRight, BottomLeft) """

        top_left = self.mgr.get_channel_samples('tl')
        top_right = self.mgr.get_channel_samples('tr')
        bottom_right = self.mgr.get_channel_samples('br')
        bottom_left = self.mgr.get_channel_samples('bl')
        return top_left, top_right, bottom_right, bottom_left

    def get_x(self):
        """ Returns COPx computed from raw sensor data and adds 'x' channel to ReadManager object"""

        top_left, top_right, bottom_right, bottom_left = self.get_raw_signal()
        x, y = wii_utils.get_x_y(top_left, top_right, bottom_right, bottom_left)
        samples = self.mgr.get_samples()
        chann_names = self.mgr.get_param('channels_names')
        self.mgr.set_samples(np.vstack((samples,x)), chann_names + [u'x'])      
        chann_off = self.mgr.get_param('channels_offsets')
        self.mgr.set_param('channels_offsets',chann_off + [u'0.0'])
        chann_gain = self.mgr.get_param('channels_gains')
        self.mgr.set_param('channels_gains',chann_gain + [u'1.0'])
        return x

    def get_y(self):
        """ Returns COPy computed from raw sensor data and adds 'y' channel to ReadManager object """
        top_left, top_right, bottom_right, bottom_left = self.get_raw_signal()
        x, y = wii_utils.get_x_y(top_left, top_right, bottom_right, bottom_left)
        samples = self.mgr.get_samples()
        chann_names = self.mgr.get_param('channels_names')
        self.mgr.set_samples(np.vstack((samples,y)), chann_names + [u'y'])
        chann_off = self.mgr.get_param('channels_offsets')
        self.mgr.set_param('channels_offsets',chann_off + [u'0.0'])
        chann_gain = self.mgr.get_param('channels_gains')
        self.mgr.set_param('channels_gains',chann_gain + [u'1.0'])
        return y

    def get_timestamps(self):
        """ Returns timestamps channel """
        
        return self.mgr.get_channel_samples('TSS')