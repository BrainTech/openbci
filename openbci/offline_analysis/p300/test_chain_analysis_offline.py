#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os, os.path, sys
from scipy import *
import unittest

from data_storage import read_manager, read_info_source, read_data_source, read_tags_source
from openbci.offline_analysis import offline_analysis_logging as logger
LOGGER = logger.get_logger("test_chain_analysis_offline", "info")

 

import chain_analysis_offline as ch

def get_fake_manager(number_of_channels, channel_len):
    """
    Return read manager with samples:
    [
       [1 2 3 ... channel_len],
       [10 20 30 ... 10*channel_len]
       ...
       [10^number_of_channels ... ]
    ]
    """
    new_samples = zeros((number_of_channels, channel_len))
    start_i = 1
    for ch in range(number_of_channels):
        new_samples[ch, :] = range(start_i, start_i*(channel_len+1), start_i)
        start_i = 10*start_i
    
    new_tags = []

    new_params = {}
    new_params['channels_names'] = ['CH'+str(i) for i in range(number_of_channels)]
    new_params['channels_numbers'] = [str(i) for i in range(number_of_channels)]
    new_params['channels_gains'] = [str(1+i/10.0) for i in range(number_of_channels)]
    new_params['channels_offsets'] = [str(i/10.0) for i in range(number_of_channels)]
    new_params['number_of_channels'] = str(number_of_channels)
    new_params['number_of_samples'] = str(channel_len*number_of_channels)
    new_params['sampling_frequency'] = str(128.0)

    info_source = read_info_source.MemoryInfoSource(new_params)
    tags_source = read_tags_source.MemoryTagsSource(new_tags)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)


class ModTest(unittest.TestCase):
    def setUp(self):
        self.TEST_READ_SIGNAL = True
        self.TEST_EXCLUDE_CHANNELS = True
        self.TEST_LEAVE_CHANNELS = True
        self.TEST_MONTAGE = True
        self.TEST_NORMALIZE = True
        
    def test_read_signal(self):
        if not self.TEST_READ_SIGNAL:
            return 
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_longer_8trials2'
        f2 = {
            'info': os.path.join(dr2, f2_name+'_10HZ.obci.xml'),
            'data': os.path.join(dr2, f2_name+'_10HZ.obci.bin'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        
        r = ch.ReadSignal(f2)
        mgrs = r.process()
        self.assertEqual(len(mgrs), 1)
        self.assertEqual(len(mgrs[0].get_tags()), 1574)
        self.assertEqual(int(mgrs[0].get_param('number_of_channels')), 24)
        sample = None
        for s in mgrs[0].iter_samples():
            sample = s
            break
        self.assertEqual(int(sample[3]), 4517)
        LOGGER.info("Signal reader tested!")

    def test_exclude_channels(self):
        if not self.TEST_EXCLUDE_CHANNELS:
            return

        mgr = get_fake_manager(5, 10)
        e = ch.ExcludeChannels(['CH2', 'CH4'])
        new_mgr = e.process([mgr])[0]

        self.assertEqual(new_mgr.get_param('number_of_channels'), '3')
        self.assertEqual(new_mgr.get_param('number_of_samples'), str(3*10))
        self.assertEqual(new_mgr.get_param('channels_names'), ['CH0', 'CH1', 'CH3'])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[0], mgr.get_channel_samples('CH3')[0])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[2], mgr.get_channel_samples('CH3')[2])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[2], 3000.0)
        self.assertEqual(new_mgr.get_channel_samples('CH0')[3], mgr.get_channel_samples('CH0')[3])
        self.assertEqual(new_mgr.get_param('channels_gains'), ['1.0', '1.1', '1.3'])
        LOGGER.info("ExcludeChannels tested!")


    def test_leave_channels(self):
        if not self.TEST_LEAVE_CHANNELS:
            return

        mgr = get_fake_manager(5, 10)
        e = ch.LeaveChannels(['CH0', 'CH1', 'CH3'])
        new_mgr = e.process([mgr])[0]
        self.assertEqual(new_mgr.get_param('number_of_channels'), '3')
        self.assertEqual(new_mgr.get_param('number_of_samples'), str(3*10))
        self.assertEqual(new_mgr.get_param('channels_names'), ['CH0', 'CH1', 'CH3'])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[0], mgr.get_channel_samples('CH3')[0])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[2], mgr.get_channel_samples('CH3')[2])
        self.assertEqual(new_mgr.get_channel_samples('CH3')[2], 3000.0)
        self.assertEqual(new_mgr.get_channel_samples('CH0')[3], mgr.get_channel_samples('CH0')[3])
        self.assertEqual(new_mgr.get_param('channels_gains'), ['1.0', '1.1', '1.3'])
        LOGGER.info("LeaveChannels tested!")

    def test_montage(self):
        if not self.TEST_MONTAGE:
            return
        #test csa
        mgr = get_fake_manager(3, 10)
        e = ch.Montage(montage_type='common_spatial_average')
        new_mgr = e.process([mgr])[0]
        self.assertEqual(
            new_mgr.get_channel_samples('CH0')[0],
            1.0 - (10.0 + 100.0)/2)
        self.assertEqual(
            new_mgr.get_channel_samples('CH2')[5],
            600.0 - (6.0 + 60.0)/2)


        mgr = get_fake_manager(9, 10)
        e = ch.Montage(montage_type='common_spatial_average')
        new_mgr = e.process([mgr])[0]
        
        self.assertEqual(mgr.get_channel_samples('CH5')[8],
                         900000.0)
        self.assertEqual(mgr.get_channel_samples('CH5')[8],
                         mgr.get_samples()[5, 8])
        self.assertEqual(
            new_mgr.get_channel_samples('CH5')[8],
            mgr.get_samples()[5, 8] - \
                sum([mgr.get_samples()[i, 8] for i in range(9) if i != 5])/8.0)

        self.assertEqual(
            new_mgr.get_channel_samples('CH5')[8],
            900000.0 - \
                sum([9*(10**i) for i in range(9) if i != 5])/8.0)
            
        #test ears
        mgr = get_fake_manager(9, 10)
        e = ch.Montage(montage_type='ears', l_ear_channel='CH1', r_ear_channel='CH2')
        new_mgr = e.process([mgr])[0]
        self.assertEqual(
            new_mgr.get_samples()[4, 0],
            mgr.get_samples()[4, 0] - \
                (mgr.get_samples()[1, 0] + mgr.get_samples()[2,0])/2)
            
        LOGGER.info("Montage tested!")

    def test_normalize(self):
        if not self.TEST_NORMALIZE:
            return
        mgr = get_fake_manager(3, 10)
        e = ch.Normalize(norm=2)
        new_mgr = e.process([mgr])[0]

        import PyML
        data = PyML.VectorDataSet(mgr.get_samples())
        data.normalize(2)
        for i in range(3):
            for j in range(10):
                self.assertAlmostEqual(new_mgr.get_samples()[i, j],
                                 data.getMatrix()[i, j])

        LOGGER.info("Normalize tested!")



if __name__ == '__main__':
    unittest.main()

