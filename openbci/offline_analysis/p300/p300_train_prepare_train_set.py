from offline_analysis import smart_tag_definition
from offline_analysis import smart_tags_manager
from offline_analysis.erp import erp_avg
import sys, os, os.path, random
import scipy

START_SEC_OFFSET = -0.1
DURATION = 0.6
TARGET_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name=u'target', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
NON_TARGET_DEF = smart_tag_definition.SmartTagDurationDefinition(start_tag_name='non-target', 
                                                          start_offset=START_SEC_OFFSET, end_offset=0, duration=DURATION)
class Averager(object):
    def get_averaged_samples(self, p_train_set, p_num_per_avg, p_start_samples_to_norm=0):
        """
        Input:
        - p_train_set: a list of dicts with keys:
        - - 'letter' - target letter (string)
        - - 'target' - a list of target smart tags for this letter
        - - 'non-target' - a list of non-target smart tags for this letter

        - p_num_per_avg - a number of trials to be averaged

        OUTPUT:
        - A two dimensional array, where:
        - - every column corresponds to channel
        - - every row corresponds to averaged signal for target or non-tarteg
        - A one dimensional array, where:
        - - every element row represents class: 1 - target, -1 - non-target for
            corresonding element in above 2dim array
        """
        pass

class RandomAverager(object):
    def get_averaged_samples(self, p_train_set, p_num_per_avg, p_start_samples_to_norm=0):
        """
        >>> dr = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/numbered_squares/'
        
        >>> f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBERS_CATDOGFISHWATERBOWL_longer_8trials'
        
        >>> f2 = {'info': os.path.join(dr, f2_name+'.obci.filtered.xml'), 'data': os.path.join(dr, f2_name+'_10HZ.obci.bin'), 'tags':os.path.join(dr, f2_name+'.obci.arts_free.svarog.tags')}
        
        >>> t = extract_trials_from_file(f2)
        
        >>> avg = RandomAverager()
        
        >>> s, c = avg.get_averaged_samples(t, 5)
        
        >>> sm = sum([len(i['target']) for i in t])/5+sum([len(i['non-target']) for i in t])/5
        
        >>> len(s[0]) == sm == len(c)
        True
        
        >>> len(s) == 24
        True
        
        """   
        # Gather target and non-target tag to separate collections
        target_tags = []
        non_target_tags = []
        for i_set in p_train_set:
            target_tags += i_set['target']
            non_target_tags += i_set['non-target']

        # shuffle both collections
        random.shuffle(target_tags)
        random.shuffle(non_target_tags)

        # Define some crucial variables
        n_target = len(target_tags) / p_num_per_avg
        n_non_target = len(non_target_tags) / p_num_per_avg
        avg_size = len(target_tags[0].get_samples()[0])
        ch_num = len(target_tags[0].get_samples())

        # Define to-be-returned variables:
        
        # an array of numbers representing trials classes (target 1, non-target -1)
        ret_classes = scipy.zeros(n_non_target + n_target)

        # A list of arrays (for every channel)
        # One array is a 2dim array with:
    
        ret_arrs = []
        ret_arr_index = 0
        for i in range(ch_num):
            ret_arrs.append(scipy.zeros((n_target + n_non_target, avg_size)))

        # Fill ret_arss
        i = 0
        while i/p_num_per_avg < n_target:
            avg_arr = erp_avg.get_normalised_avgs(target_tags[i:(i+p_num_per_avg)], 
                                                  p_start_samples_to_norm,
                                                  avg_size)
            for j in range(ch_num):
                ret_arrs[j][ret_arr_index, :] = avg_arr[j, :]
            ret_classes[ret_arr_index] = 1.0
            ret_arr_index += 1
            i += p_num_per_avg

        i = 0
        while i/p_num_per_avg < n_non_target:
            avg_arr = erp_avg.get_normalised_avgs(non_target_tags[i:(i+p_num_per_avg)], 
                                         p_start_samples_to_norm,
                                         avg_size)
            for j in range(ch_num):
                ret_arrs[j][ret_arr_index, :] = avg_arr[j, :]
            ret_classes[ret_arr_index] = -1.0
            ret_arr_index += 1
            i += p_num_per_avg

        #print("R: ", str(ret_arr_index), ", N: ", str(n_target + n_non_target))        
        assert(ret_arr_index == n_target + n_non_target)
        return ret_arrs, ret_classes
        

    
def extract_trials_from_file(p_files):
    """
    Extract data from p_files and return it in format:
    - a list of dictionaries, where every subsequent dictionary corresponds to one target-letter 
      in a training session.
      every dict has fields as follows:
      - 'letter' - a string for a target-letter
      - 'target' - a list of smart tags representing target-epochs - when a person was looking at the target letter
         and a blink was on that letter
      - 'non-target'- a list of smart tags representing non-target-epochs - when a person was looking at the target letter
         but blink was somewere else

      eg:
      {'letter':'C', 'target': [tag, tag, tag], 'non-target': [tag, tag]}


    >>> dr = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/numbered_squares/'

    >>> f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBERS_CATDOGFISHWATERBOWL_longer_8trials'

    >>> f2 = {'info': os.path.join(dr, f2_name+'.obci.filtered.xml'), 'data': os.path.join(dr, f2_name+'_10HZ.obci.bin'), 'tags':os.path.join(dr, f2_name+'.obci.arts_free.svarog.tags')}

    >>> t = extract_trials_from_file(f2)

    >>> [len(i['target']) for i in t]
    [11, 8, 4, 12, 10, 11, 13, 13, 10, 11, 13, 12, 11, 14, 12, 8, 16, 15, 15]

    >>> [len(i['non-target']) for i in t]
    [51, 64, 28, 78, 50, 56, 57, 62, 57, 57, 75, 59, 61, 66, 62, 51, 73, 73, 74]

    """

    mgr_target = smart_tags_manager.SmartTagsManager(TARGET_DEF, p_files['info'], p_files['data'], p_files['tags'])
    mgr_non_target = smart_tags_manager.SmartTagsManager(NON_TARGET_DEF, None, None, None, mgr_target.get_read_manager()) 

    letter_tag_sets = []
    target_tags = mgr_target.get_smart_tags()
    target_tags_len = len(target_tags)
    
    assert(len(target_tags) > 0)
    
    # First gather target tags for subsequent targets (letters)
    l_prev_letter = target_tags[0]['desc']['letter']
    l_curr_set = {'target':[], 'non-target': [], 'letter': l_prev_letter}
    
    for i_target in target_tags:
        if i_target['desc']['letter'] == l_prev_letter:
            # Still the same letter ..
            l_curr_set['target'].append(i_target)
        else:
            # A new letter occured, init a new set
            letter_tag_sets.append(l_curr_set)
            l_curr_set = {'target':[], 'non-target':[]}
            l_curr_set['letter'] = i_target['desc']['letter']
            l_curr_set['target'].append(i_target)
        l_prev_letter = i_target['desc']['letter']

    letter_tag_sets.append(l_curr_set)
            
    # Now gather non-target tags corresponding to subsequent target tags
    non_target_tags = mgr_non_target.get_smart_tags()
    non_target_tags_len = len(non_target_tags)
    for i in range(len(letter_tag_sets)):
        curr_set = letter_tag_sets[i]
        try:
            next_set = letter_tag_sets[i+1]
        except IndexError:
            next_set = None

        if not (next_set is None):
            start_t = curr_set['target'][0]['start_timestamp']
            len_t = next_set['target'][0]['start_timestamp'] - start_t
            curr_set['non-target'] = mgr_non_target.get_smart_tags(None, start_t, len_t)

        else:
            # curr_set is the last set
            curr_set['non-target'] = mgr_non_target.get_smart_tags(None,
                                                                   curr_set['target'][0]['start_timestamp'],
                                                                   sys.float_info.max)
    return letter_tag_sets
                                                                   
      
def downsample_train_set(p_train_set, leave_every=1):
    """

    >>> set1, set2 = ([[1,2,3,4,5], [10, 20, 30, 40, 50]], [[6,7,8,9,10], [60,70,80,90,100]])
    
    >>> st = [scipy.array(set1), scipy.array(set2)]

    >>> downsample_train_set(st)
    [array([[  1.,   2.,   3.,   4.,   5.],
           [ 10.,  20.,  30.,  40.,  50.]]), array([[   6.,    7.,    8.,    9.,   10.],
           [  60.,   70.,   80.,   90.,  100.]])]

    >>> downsample_train_set(st, 2)
    [array([[  1.,   3.,   5.],
           [ 10.,  30.,  50.]]), array([[   6.,    8.,   10.],
           [  60.,   80.,  100.]])]

    >>> downsample_train_set(st, 3)
    [array([[  1.,   4.],
           [ 10.,  40.]]), array([[  6.,   9.],
           [ 60.,  90.]])]

    >>> downsample_train_set(st, 4)
    [array([[  1.,   5.],
           [ 10.,  50.]]), array([[   6.,   10.],
           [  60.,  100.]])]

    """
    assert(leave_every > 0)
    assert(len(p_train_set) > 0)
    ret_train_set = []
    # Determine ret feature len:
    ret_feature_len = 0
    samples_len = len(p_train_set[0])
    i = 0
    left_inds = []
    while i < len(p_train_set[0][0, :]):
        left_inds.append(i)
        ret_feature_len += 1
        i += leave_every

    # For every channel downsample its features...
    for i_channel_set in p_train_set:
        l_new_channel_set = scipy.array([scipy.zeros(ret_feature_len) for i in range(samples_len)])
        for i, i_feature in enumerate(i_channel_set):
            for j, ind in enumerate(left_inds):
                l_new_channel_set[i, j] = i_feature[ind]
        ret_train_set.append(l_new_channel_set)
    return ret_train_set
            
  

def get_train_set(files, num_per_avg=5, start_samples_to_norm=0, downsample_level=1):
    t = extract_trials_from_file(files)
    avg = RandomAverager()
    s, c = avg.get_averaged_samples(t, num_per_avg, start_samples_to_norm)
    if downsample_level > 1:
        s = downsample_train_set(s, downsample_level)
    return s, c




TEST = True
def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")
    

if __name__ == '__main__':
    if TEST:
        test()
        sys.exit(0)
    dr = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/numbered_squares/'
    f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBERS_CATDOGFISHWATERBOWL_longer_8trials'
    f2 = {
        'info': os.path.join(dr, f2_name+'.obci.filtered.xml'),
        #'info': os.path.join(dr, f2_name+'.obci.xml'),
        'data': os.path.join(dr, f2_name+'_10HZ.obci.bin'),
        #'data': os.path.join(dr, f2_name+'.obci.bin'),

        'tags':os.path.join(dr, f2_name+'.obci.arts_free.svarog.tags')
        #'info': os.path.join(dr, f_name+'.obci.info'),
        #'data': os.path.join(dr, f_name+'.obci.dat'),
        #'tags':os.path.join(dr, f_name+'.obci.tags')
       }



    t = extract_trials_from_file(f2)
    target_tags_len = 0
    non_target_tags_len = 0
    for i in t:
        print(i['letter'], " / ", str(len(i['target'])), 
              " / ", str(len(i['non-target'])))
        target_tags_len += len(i['target'])
        non_target_tags_len +=len(i['non-target'])

    x1 = [len(i['target']) for i in t]
    x2 = [len(i['non-target']) for i in t]
    print(x1)
    print(x2)
    print("CMPUTED TARGET LEN: ", str(target_tags_len), ", COMPUTED NON_TARGET LEN: ", str(non_target_tags_len))


