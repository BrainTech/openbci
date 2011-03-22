#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from scipy import *
from scipy import linalg
from scipy import signal
import pylab
import PyML
import copy
from data_storage import read_manager, read_info_source, read_data_source, read_tags_source
from offline_analysis import smart_tag_definition, smart_tags_manager, averaged_epochs

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

def segment(mgr, classes, start_offset, duration):
    defs = []
    for i_start_tag in classes:
        defs.append(smart_tag_definition.SmartTagDurationDefinition(
                start_tag_name=i_start_tag, start_offset=start_offset, 
                end_offset=0, duration=duration))
    smart_mgr = smart_tags_manager.SmartTagsManager(defs, None, None, None, mgr)
    return smart_mgr.get_smart_tags()



def average(mgrs, bin_selectors, bin_names, size, baseline=0.0, strategy='random'):
    if strategy == 'random':
        return random_average(mgrs, bin_selectors, bin_names, size, baseline)


def random_average(mgrs, bin_selectors, bin_names, size, baseline=0.0):
    # Bins correspond to every 'class' of mgrs to be averaged
    # inside classes.
    bins = [[] for i in range(len(bin_selectors))]
    sampling = float(mgrs[0].get_param('sampling_frequency'))
    samples_to_norm = int(sampling*baseline)
    # Place every manager in some bin, selector is a function
    # that returnes true if given manager should be in the bin
    for mgr in mgrs:
        for i, selector in enumerate(bin_selectors):
            try:
                if selector(mgr):
                    bins[i].append(mgr)
            except TypeError:
                # if selector is not a function lets assume
                # that this is mgr name (string)
                if mgr['name'] == selector:
                    bins[i].append(mgr)

    avg_mgrs = []
    info_template = bins[0][0].info_source
    avg_len = len(bins[0][0].get_samples()[0])
    # Shuffle and avg bins
    for bin_ind, bin in enumerate(bins):
        random.shuffle(bin)
        i = 0
        while i+size <= len(bin):
            avg_mgrs.append(
                averaged_epochs.AveragedEpochs(
                                bin[i:(i+size)],
                                copy.deepcopy(info_template),
                                bin_names[bin_ind],
                                samples_to_norm,
                                avg_len
                                )
                )

            i += size
    return avg_mgrs


def prepare_train_set(mgrs):
    assert(len(mgrs) > 0)
    l = PyML.Labels([i.get_param('epoch_name') for i in mgrs])
    train_data = zeros((len(mgrs), len(mgrs[0].get_samples()[0])))
    for i, mgr in enumerate(mgrs):
        # Only the first channel is taken to consideration
        train_data[i, :] = mgr.get_samples()[0]

    train_set = PyML.VectorDataSet(train_data, L=l)
    return train_set
    

def svm(train_data, C, Cmode, kernel, folds=5, ret='balancedSuccessRate'):
    s = PyML.svm.SVM(C=C, Cmode=Cmode, arg=kernel)
    if ret == 'balancedSuccessRate':
        return s.stratifiedCV(train_data, folds).getBalancedSuccessRate()
    else:
        return s.stratifiedCV(train_data, folds)




def _p300_prepare_folded_mgrs(all_target_mgrs, all_non_target_mgrs, folds, non_target_per_target):
    # Determine fold parameters
    target_perm = range(len(all_target_mgrs))
    target_fold_size = len(all_target_mgrs)/folds
    random.shuffle(target_perm)
    # In every fold we take target_fold_size target managers as test set
    # And non_target_per_target*target_fold_size non-target managers as test set,
    # lets prepare non-target managers indices...

    non_target_fold_size = target_fold_size*non_target_per_target
    tmp = range(len(all_non_target_mgrs))
    random.shuffle(tmp)
    non_target_perm = list(tmp)

    # len(non_target_perm) must be = len(target_perm)*non_target_per_target
    # ensure this ...
    to_extend = len(target_perm)*non_target_per_target - len(non_target_perm)
    if to_extend > 0:
        non_target_perm += tmp[:to_extend]
    elif to_extend < 0:
        non_target_perm = non_target_perm[:to_extend]

    assert(len(non_target_perm) == len(target_perm)*non_target_per_target)
    
    folded_data = []
    for fold in range(folds):
        # generate fold train and test set
        if fold < folds - 1:
            t_test_inds = target_perm[target_fold_size*fold:target_fold_size*(fold+1)]
            nt_test_inds = non_target_perm[non_target_fold_size*fold:non_target_fold_size*(fold+1)]
        else:
            t_test_inds = target_perm[target_fold_size*fold:]
            nt_test_inds = non_target_perm[non_target_fold_size*fold:]

        t_test_mgrs = [all_target_mgrs[i] for i in t_test_inds]
        nt_test_mgrs = [all_non_target_mgrs[i] for i in nt_test_inds]
        t_train_mgrs = [all_target_mgrs[i] for i in range(len(all_target_mgrs)) if not i in t_test_inds]
        nt_train_mgrs = [all_non_target_mgrs[i] for i in range(len(all_non_target_mgrs)) if not i in nt_test_inds]
        assert(len(t_test_mgrs)*non_target_per_target == len(nt_test_mgrs))

        folded_data.append(
            ((t_train_mgrs, nt_train_mgrs), (t_test_mgrs, nt_test_mgrs))
            )
    return folded_data


def _p300_verify_svm_one_fold(t_train_mgrs, nt_train_mgrs,
                              t_test_mgrs, nt_test_mgrs,
                              non_target_per_target,
                              C, Cmode, kernel):

    assert(len(t_test_mgrs)*non_target_per_target == len(nt_test_mgrs))
    s = PyML.svm.SVM(C=C, Cmode=Cmode, arg=kernel)

    # Train classifier on a train set...
    train_data =  t_train_mgrs+nt_train_mgrs
    train_vect = zeros((len(train_data), len(train_data[0].get_samples()[0])))
    train_labels_vect = []
    for i, mgr in enumerate(train_data):
        train_labels_vect.append(mgr.get_param('epoch_name'))
        train_vect[i, :] = mgr.get_samples()[0]
    s.train(PyML.VectorDataSet(train_vect,
                               L=PyML.Labels(train_labels_vect)))
    
    # test classifier on a test set
    # grab two elements of target test set and 2*non_target_per_target elements
    # of non-target test set ....
    succ = 0
    fail = 0
    i = 0
    while i+1 < len(t_test_mgrs):
        t1 = t_test_mgrs[i]
        ns1 = nt_test_mgrs[i*non_target_per_target:(i+1)*non_target_per_target]
        whatever, t1_value = s.classify(PyML.VectorDataSet(t1.get_samples()), 0)
        ns1_value = max([s.classify(PyML.VectorDataSet(n1.get_samples()), 0)[1] for n1 in ns1])

        t2 = t_test_mgrs[i+1]
        ns2 = nt_test_mgrs[(i+1)*non_target_per_target:(i+2)*non_target_per_target]
        whatever, t2_value = s.classify(PyML.VectorDataSet(t2.get_samples()), 0)
        ns2_value = max([s.classify(PyML.VectorDataSet(n2.get_samples()), 0)[1] for n2 in ns2])

        # Check if the decision was good ...
        if t1_value > ns1_value and t2_value > ns2_value:
            succ += 1
        else:
            fail += 1
        i+=2
    return succ, fail


def p300_verify_svm(mgrs, C, Cmode, kernel, folds=5, non_target_per_target=6):
    assert(len(mgrs) > 0)
    all_target_mgrs = [mgr for mgr in mgrs if mgr.get_param('epoch_name') == 'target']
    all_non_target_mgrs = [mgr for mgr in mgrs if mgr.get_param('epoch_name') == 'non-target']
    folds_data = _p300_prepare_folded_mgrs(all_target_mgrs, all_non_target_mgrs, folds, non_target_per_target)

    succ = []
    fail = []
    for data in folds_data:
        s, f = _p300_verify_svm_one_fold(
            data[0][0], data[0][1],
            data[1][0], data[1][1],
            non_target_per_target,
            C, Cmode, kernel)
        succ.append(s)
        fail.append(f)

    avg_succ = sum([float(succ[i])/(succ[i]+fail[i]) for i in range(folds)])/folds
    return avg_succ, (succ, fail)
        

                



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
	



def plot(mgr, channel):
    ch = mgr.get_channel_samples(channel)
#    mgr.save_to_file('./', 'dupa')
    pylab.plot(ch)
    pylab.show()
