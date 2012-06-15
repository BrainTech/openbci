#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import scipy
import sys

def store_avgs_for_svarog(avgs, f_dir='./', f_name='svarog'):
    """Saver data file with len(avgs) channels and with data from avgs."""
    from openbci.offline_analysis.obci_signal_processing.signal import data_raw_write_proxy as fp
    w = fp.DataRawWriteProxy(f_name, f_dir, 'p300')
    max_len = len(max(avgs))
    for i in range(max_len):
        for j in range(len(avgs)):
            try:
                number = avgs[j][i]
            except:
                number = 0.0
            w.data_received(number)
    w.finish_saving()



def get_avgs(p_st_manager):
    """Return a two dimensional list of averaged signals
    from every channel.
    A number of averaged signals is determined by a number of 
    smart tags in smart tags manager - p_st_manager.
    A number of channels is determined by smart tag.

    DEPRECIATED - USE get_normalised_avgs!!!!!

    """
    l_num_of_channels = p_st_manager.num_of_channels
    l_channels_sums = [[0.0] for i in range(l_num_of_channels)]
    # l_channels_sum will be a list of lists, 
    # eg: [
    #        [2,1,2,4,5],
    #        [23,5,6,7,4],
    #        ...
    #      ]
    # where list[i][j] is an average among all smart tags for j sample, 
    # for i channel
    l_st_num = 0
    for i_st in p_st_manager:
        l_st_num += 1
        l_channels_data = i_st.get_samples()
        # l_channels_data is a list of list, just like l_channels_sums
        for i, i_ch_samples in enumerate(l_channels_data):
            for j, i_ch_sample in enumerate(i_ch_samples):
                try:
                    l_channels_sums[i][j]
                except IndexError:
                    l_channels_sums[i].append(0.0)
                l_channels_sums[i][j] = l_channels_sums[i][j] + i_ch_sample
    for i_one_ch_sums in l_channels_sums:
        for i, i_sum in enumerate(i_one_ch_sums):
            i_one_ch_sums[i] = i_sum/l_st_num

    return l_channels_sums




def get_normalised_avgs(p_samples_source, p_start_samples_to_norm=0, p_avg_len=None):
    """Return a two dimensional array of averaged signals
    from every channel, according to p_samples_source.
   
    Parameters:
    - p_samples_source: an iterable object that during iteration returns
      objects that respond to get_samples() method. Eg. it migth be SmartTagsManager
      or a list of MemoryDataSource objects.
    - p_start_samples_to_norm - if > 0, then for every averaged channel
      substract a mean of its starting p_start_samples_to_norm points from every sample.
    - p_avg_len - normally p_samples_source should contain samples whe the same channels count
      and the same channels size; hovewer if there are differences one migth enforce 
      returned array size by p_avg_len.


    >>> from openbci.offline_analysis.obci_signal_processing.signal import read_data_source as s

    >>> ss = [s.MemoryDataSource([[1., 2., 3.],[4., 5., 6.]]), s.MemoryDataSource([[10., 20., 30.], [40., 50., 60.]]), s.MemoryDataSource([[100., 200., 300.], [400., 500., 600.]])]

    >>> get_normalised_avgs(ss)
    array([[  37.,   74.,  111.],
           [ 148.,  185.,  222.]])

    >>> get_normalised_avgs(ss, 0, 4)
    array([[  37.,   74.,  111.,    0.],
           [ 148.,  185.,  222.,    0.]])

    >>> get_normalised_avgs(ss, 1)
    array([[  0.,  37.,  74.],
           [  0.,  37.,  74.]])

    >>> get_normalised_avgs(ss, 2)
    array([[-18.5,  18.5,  55.5],
           [-18.5,  18.5,  55.5]])

    """
    assert(p_start_samples_to_norm >= 0)
    assert(p_avg_len == None or p_avg_len > 0)

    #l_num_of_channels = p_st_manager.num_of_channels
    i = 0
    for i_source in p_samples_source:
        if i == 0:
            # initialize to-be-returned array
            if p_avg_len is None:
                l_ret_arr_len = len(i_source.get_samples()[0])
            else:
                l_ret_arr_len = p_avg_len
            l_ret_arr_ch_len = len(i_source.get_samples())
            l_ret_arr = scipy.zeros((l_ret_arr_ch_len, l_ret_arr_len))

        i += 1
        l_s_len = len(i_source.get_samples()[0])
        assert(len(i_source.get_samples()) == l_ret_arr_ch_len)
        # Subsequent smart tags migh have different samples lenght (same num_of_channels is a must!).
        # In order not to blow out, lets just ignore a tail of longer collection...
        if l_ret_arr_len == l_s_len:
            l_ret_arr[:] = l_ret_arr + i_source.get_samples()
        elif l_ret_arr_len > l_s_len:
            l_ret_arr[:, :l_s_len] = l_ret_arr[:, :l_s_len] + i_source.get_samples()
        else:
            l_ret_arr[:] = l_ret_arr + i_source.get_samples()[:, :l_ret_arr_len]

    assert(i > 0)
    # Sums are computed, now lets divide, so that we get an average
    l_ret_arr[:] = l_ret_arr/float(i)

    # Normalization - substract from the signal an average of first start_samples_to_norm samples...
    if p_start_samples_to_norm > 0:
        for i in range(len(l_ret_arr)):
            l_ret_arr[i, :] = l_ret_arr[i, :] - l_ret_arr[i, :p_start_samples_to_norm].mean()
    return l_ret_arr

def normalise_array(arr, boundary=1.0):
    """After that every column (channel) in arr
    will have values in (-boundary, boundary).

    >>> a = scipy.array([[1.,2.,3.,4.,5.], [10., 20., 30., 40., 50.]])

    >>> normalise_array(a)
    array([[ 0.2,  0.4,  0.6,  0.8,  1. ],
           [ 0.2,  0.4,  0.6,  0.8,  1. ]])


    """
    for i in range(len(arr)):
        arr[i, :] = (boundary*arr[i, :])/abs(arr[i, :]).max()
    return arr

def std_normalise_array(arr):
    """After that every column (channel) in arr
    will have mean=0, std = 1.

    >>> a = scipy.array([[1.,2.,3.,4.,5.], [10., 20., 30., 40., 50.]])

    >>> na = std_normalise_array(a)

    >>> scipy.std(na) == 1.0
    True

    >>> scipy.average(na) == 0.0
    True

    """
    for i in range(len(arr)):
        arr[i, :] = (arr[i, :] - scipy.average(arr[i, :]))/scipy.std(arr[i, :])
    return arr

TEST = True
def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")


if __name__ == '__main__':
    if TEST:
        test()
        sys.exit(0)
