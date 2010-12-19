#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from scipy import *
import copy
from data_storage import read_manager, read_info_source, read_data_source, read_tags_source

def exclude_channels(mgr, channels):
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
    chans = copy.deepcopy(mgr.get_param('channels_names'))
    for leave in channels:
        chans.remove(leave)
    return exclude_channels(mgr, chans)
    
    

def montage(mgr, montage_type, **montage_params):
    if montage_type == 'common_spatial_average':
        return montage_csa(mgr, **montage_params)
    elif montage_type == 'ears':
        return montage_ears(mgr, **montage_params)
    elif montage_type == 'custom':
        return montage_custom(mgr, **montage_params)
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
    print("AAAAAAAAAAAAAAAAAAAAAA ")
    print(left_index, ' / ', right_index)
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

def montage_custom(mgr, montage_matrix):
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
	
