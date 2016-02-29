#!/usr/bin/env python
# -*- coding: utf-8 -*-
# based on obci.analysis.p300.analysis_offline
# Marian Dovgialo
from scipy import *
from scipy import linalg
import numpy as np
from scipy import signal
import copy
from obci.analysis.obci_signal_processing.signal import read_info_source
from obci.analysis.obci_signal_processing.signal import read_data_source
from obci.analysis.obci_signal_processing.tags import read_tags_source
from obci.analysis.obci_signal_processing import read_manager

def mgr_filter(mgr, wp, ws, gpass, gstop, analog=0, ftype='ellip', output='ba', unit='hz', use_filtfilt=False, meancorr=1.0):
    if unit == 'radians':
        b,a = signal.iirdesign(wp, ws, gpass, gstop, analog, ftype, output)
    elif unit == 'hz':
        nyquist = float(mgr.get_param('sampling_frequency'))/2.0
        try:
            wp = wp/nyquist
            ws = ws/nyquist
        except TypeError:
            wp = [i/nyquist for i in wp]
            ws = [i/nyquist for i in ws]

        b,a = signal.iirdesign(wp, ws, gpass, gstop, analog, ftype, output)
    if use_filtfilt:    
        from scipy.signal import filtfilt
        #samples_source = read_data_source.MemoryDataSource(mgr.get_samples(), False)
        for i in range(int(mgr.get_param('number_of_channels'))):
            print("FILT FILT CHANNEL "+str(i))
            mgr.get_samples()[i,:] = signal.filtfilt(b, a, mgr.get_samples()[i]-np.mean(mgr.get_samples()[i])*meancorr)
        samples_source = read_data_source.MemoryDataSource(mgr.get_samples(), False)
    else:
        print("FILTER CHANNELs")
        filtered = signal.lfilter(b, a, mgr.get_samples())
        print("FILTER CHANNELs finished")
        samples_source = read_data_source.MemoryDataSource(filtered, True)

    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    new_mgr = read_manager.ReadManager(info_source, samples_source, tags_source)
    return new_mgr
#####

def leave_channels_array(arr, channels, available):
    '''
    :param arr: - 2d array of eeg data channels x samples
    :param channels: - channels to leave,
    :param available: - channel names in data
    '''
    exclude = list(set(available).difference(set(channels)))
    new_samples, new_channels = exclude_channels_array(
                                                arr, exclude, available)
    return new_samples, new_channels

def exclude_channels_array(arr, channels, available):
    '''arr - 2d array of eeg data channels x samples
    channels - channels to exclude,
    available - channel names in data'''
    exclude = set(channels)
    channels = list(set(available).intersection(exclude))
    
    ex_channels_inds = [available.index(ch) for ch in channels]
    assert(-1 not in ex_channels_inds)
    new_samples = zeros((len(available) - len(channels),
                         len(arr[0])))
                         
    
    new_ind = 0
    new_channels = []
    for ch_ind, ch in enumerate(arr):
        if ch_ind in ex_channels_inds:
            continue
        else:
            new_samples[new_ind, :] = ch
            new_channels.append(available[ch_ind])

            new_ind += 1
    return new_samples, new_channels

def exclude_channels(mgr, channels):
    '''exclude all channels in channels list'''
    available = set(mgr.get_param('channels_names'))
    exclude = set(channels)
    channels = list(available.intersection(exclude))
    
    new_params = copy.deepcopy(mgr.get_params())
    samples = mgr.get_samples()
    new_tags = copy.deepcopy(mgr.get_tags())
    

    ex_channels_inds = [new_params['channels_names'].index(ch) for ch in channels]
    assert(-1 not in ex_channels_inds)

    new_samples = zeros((int(new_params['number_of_channels']) - len(channels),
                         len(samples[0])))
    # Define new samples and params list values
    keys = ['channels_names', 'channels_numbers', 'channels_gains', 'channels_offsets']
    keys_to_remove = []
    for k in keys:
        try:
            #Exclude from keys those keys that are missing in mgr
            mgr.get_params()[k]
        except KeyError:
            keys_to_remove.append(k)
            continue
        new_params[k] = []

    for k in keys_to_remove:
        keys.remove(k)
    new_ind = 0
    for ch_ind, ch in enumerate(samples):
        if ch_ind in ex_channels_inds:
            continue
        else:
            new_samples[new_ind, :] = ch
            for k in keys:
                new_params[k].append(mgr.get_params()[k][ch_ind])

            new_ind += 1

    # Define other new new_params
    new_params['number_of_channels'] = str(int(new_params['number_of_channels']) - len(channels))
    new_params['number_of_samples'] = str(int(new_params['number_of_samples']) - \
                                              len(channels)*len(samples[0]))
    

    info_source = read_info_source.MemoryInfoSource(new_params)
    tags_source = read_tags_source.MemoryTagsSource(new_tags)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)


def leave_channels(mgr, channels):
    '''exclude all channels except those in channels list'''
    chans = copy.deepcopy(mgr.get_param('channels_names'))
    for leave in channels:
        chans.remove(leave)
    return exclude_channels(mgr, chans)
    

def filter(mgr, wp, ws, gpass, gstop, analog=0, ftype='ellip', output='ba', unit='radians', use_filtfilt=False):
    if unit == 'radians':
        b,a = signal.iirdesign(wp, ws, gpass, gstop, analog, ftype, output)
    elif unit == 'hz':
        sampling = float(mgr.get_param('sampling_frequency'))
        try:
            wp = wp/sampling
            ws = ws/sampling
        except TypeError:
            wp = [i/sampling for i in wp]
            ws = [i/sampling for i in ws]

        b,a = signal.iirdesign(wp, ws, gpass, gstop, analog, ftype, output)
    if use_filtfilt:    
        import filtfilt
        #samples_source = read_data_source.MemoryDataSource(mgr.get_samples(), False)
        for i in range(int(mgr.get_param('number_of_channels'))):
            print("FILT FILT CHANNEL "+str(i))
            mgr.get_samples()[i,:] = filtfilt.filtfilt(b, a, mgr.get_samples()[i])
        samples_source = read_data_source.MemoryDataSource(mgr.get_samples(), False)
    else:
        print("FILTER CHANNELs")
        filtered = signal.lfilter(b, a, mgr.get_samples())
        print("FILTER CHANNELs finished")
        samples_source = read_data_source.MemoryDataSource(filtered, True)

    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    new_mgr = read_manager.ReadManager(info_source, samples_source, tags_source)
    return new_mgr

def normalize(mgr, norm):
    if norm == 0:
        return mgr
    new_mgr = copy.deepcopy(mgr)
    for i in range(len(new_mgr.get_samples())):
        n = linalg.norm(new_mgr.get_samples()[i, :], norm)
        new_mgr.get_samples()[i, :] /= n
    return new_mgr
    

def downsample(mgr, factor):
    assert(factor >= 1)


    ch_num = len(mgr.get_samples())
    ch_len = len(mgr.get_samples()[0])

    # To be determined ...
    ret_ch_len = 0
    i = 0
    left_inds = []
    
    # Determine ret_ch_len - a size of returned channel
    while i < ch_len:
        left_inds.append(i)
        ret_ch_len += 1
        i += factor

    new_samples = array([zeros(ret_ch_len) for i in range(ch_num)])
    for i in range(ch_num):
        for j, ind in enumerate(left_inds):
            new_samples[i, j] = mgr.get_samples()[i, ind]


    info_source = copy.deepcopy(mgr.info_source)
    info_source.get_params()['number_of_samples'] = str(ret_ch_len*ch_num)
    info_source.get_params()['sampling_frequency'] = str(float(mgr.get_param('sampling_frequency'))/factor)

    tags_source = copy.deepcopy(mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)








        

                



def montage(mgr, montage_type, **montage_params):
    if montage_type == 'common_spatial_average':
        return montage_csa(mgr, **montage_params)
    elif montage_type == 'ears':
        return montage_ears(mgr, **montage_params)
    elif montage_type == 'custom':
        return montage_custom(mgr, **montage_params)
    elif montage_type == 'no_montage':
        return mgr
    else:
        raise Exception("Montage - unknown montaget type: "+str(montage_type))

def montage_csa(mgr):
    new_samples = get_montage(mgr.get_samples(),
                              get_montage_matrix_csa(int(mgr.get_param('number_of_channels'))))
    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)

def montage_ears(mgr, l_ear_channel, r_ear_channel):
    left_index = mgr.get_param('channels_names').index(l_ear_channel)
    right_index = mgr.get_param('channels_names').index(r_ear_channel)
    if left_index < 0 or right_index < 0:
        raise Exception("Montage - couldn`t find ears channels: "+str(l_ear_channel)+", "+str(r_ear_channel))

    new_samples = get_montage(mgr.get_samples(),
                              get_montage_matrix_ears(
            int(mgr.get_param('number_of_channels')),
            left_index,
            right_index
            ))
    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)
    
    
def get_channel_indexes(channels, toindex):
    '''get list of indexes of channels in toindex list as found in
    channels list'''
    indexes = []
    for chnl in toindex:
        index = channels.index(chnl)
        if index<0:
            raise Exception("Montage - couldn`t channel: "+str(chnl))
        else:
            indexes.append(index)
    return indexes
    
def montage_custom(mgr, chnls):
    '''apply custom montage to manager, by chnls'''
    indexes = []
    for chnl in chnls:
        print mgr.get_param('channels_names')
        index = mgr.get_param('channels_names').index(chnl)
        if index<0:
            raise Exception("Montage - couldn`t channel: "+str(chnl))
        else:
            indexes.append(index)

    new_samples = get_montage(mgr.get_samples(),
                              get_montage_matrix_custom(
            int(mgr.get_param('number_of_channels')),
            indexes
            ))
    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)

def montage_custom_matrix(mgr, montage_matrix):
    new_samples = get_montage(mgr.get_samples(),
                              montage_matrix)
    info_source = copy.deepcopy(mgr.info_source)
    tags_source = copy.deepcopy(mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return read_manager.ReadManager(info_source, samples_source, tags_source)
    
def get_montage(data, montage_matrix):
    """
    montage_matrix[i] = linear transformation of all channels to achieve _new_ channel i
    data[i] = original data from channel i

    >>> montage_matrix = np.array([[ 1.  , -0.25, -0.25, -0.25, -0.25], [-0.25,  1.  , -0.25, -0.25, -0.25], [-0.25, -0.25,  1.  , -0.25, -0.25],[-0.25, -0.25, -0.25,  1.  , -0.25], [-0.25, -0.25, -0.25, -0.25,  1.  ]])
    >>> data = np.array(5 * [np.ones(10)])
    >>> montage(data,montage_matrix)
    array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])


    """

    return dot(montage_matrix, data)




def get_montage_matrix_csa(n):
    """
    Return nxn array representing extraction from 
    every channel an avarage of all other channels.
    
    >>> get_montage_matrix_avg(5)
    array([[ 1.  , -0.25, -0.25, -0.25, -0.25],
           [-0.25,  1.  , -0.25, -0.25, -0.25],
           [-0.25, -0.25,  1.  , -0.25, -0.25],
           [-0.25, -0.25, -0.25,  1.  , -0.25],
           [-0.25, -0.25, -0.25, -0.25,  1.  ]])

    """ 

    factor = -1.0/(n - 1)
    mx = ones((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                mx[i, j] = factor
    return mx



def get_montage_matrix_ears(n, l_ear_index, r_ear_index):
    """
    Return nxn array representing extraction from 
    every channel an avarage of channels l_ear_index
    and r_ear_index.
    
    >>> get_montage_matrix_ears(5, 2, 4)
    array([[ 1. ,  0. , -0.5,  0. , -0.5],
           [ 0. ,  1. , -0.5,  0. , -0.5],
               [ 0. ,  0. ,  1. ,  0. ,  0. ],
               [ 0. ,  0. , -0.5,  1. , -0.5],
               [ 0. ,  0. ,  0. ,  0. ,  1. ]])
    """ 

    factor = -0.5
    mx = diag([1.0]*n)
    for i in range(n):
        for j in range(n):
            if j in [r_ear_index, l_ear_index] \
                    and j != i \
                    and not i in [r_ear_index, l_ear_index]:
                mx[i, j] = factor
    return mx

def get_montage_matrix_custom(n, indexes):
    """
    Return nxn array representing extraction from 
    every channel an avarage of channels in indexes list
    
    >>> get_montage_matrix_ears(5, 2, 4)
    array([[ 1. ,  0. , -0.5,  0. , -0.5],
           [ 0. ,  1. , -0.5,  0. , -0.5],
               [ 0. ,  0. ,  1. ,  0. ,  0. ],
               [ 0. ,  0. , -0.5,  1. , -0.5],
               [ 0. ,  0. ,  0. ,  0. ,  1. ]])
    """ 

    factor = -1.0/len(indexes)
    mx = diag([1.0]*n)
    for i in range(n):
        for j in range(n):
            if j in indexes \
                    and j != i \
                    and not i in indexes:
                mx[i, j] = factor
    return mx
