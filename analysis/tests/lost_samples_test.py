#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
import math
from obci.analysis.obci_signal_processing import read_manager
from analysis import analysis_logging as logger
LOGGER = logger.get_logger("lost_samples_test", "debug")


TEST = False

def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")

def find_lost_samples(p_read_mgr, numbers=None, spare_memory=False, saw_name="DriverSaw", saw_top=sys.float_info.max):
    """
    p_read_mgr['SAMPLE_NUMBER'] channels (or a collection numbers) 
    should contain a sequence of naturals (starting from 1)
    Check it and return all missing values.

    >>> find_lost_samples(None, [2,3,4,10,15,16,17,18,20])
    [1, 5, 6, 7, 8, 9, 11, 12, 13, 14, 19]

    """
    if p_read_mgr:
        if spare_memory:
            ch_ind = p_read_mgr.get_param('channels_names').index(saw_name)
            samples_no = []
            for samples in p_read_mgr.iter_samples():
                samples_no.append(samples[ch_ind])
        else:
            samples_no = p_read_mgr.get_channel_samples(saw_name)
        print "NUMBER OF SAMPLES RED: "+str(len(samples_no))
    else:
        samples_no = numbers

    last = samples_no[0]
    lost = []
    lost += [i for i in range(1,int(last))]
    for index, no in enumerate(samples_no[1:]):
        if no > last:
            if (no - 1) != last:
                lost += [i for i in range(int(last)+1, int(no))]
            else:
                pass
        else:
            if last == saw_top and no == 1:
                pass
            else:
                lost += ([i for i in range(int(last)+1, int(saw_top))]+[i for i in range(1, int(no))])
        last = no
    return lost

def find_lost_samples_big(p_read_mgr, numbers=None):
    """
    p_read_mgr['SAMPLE_NUMBER'] channels (or a collection numbers) 
    should contain a sequence of naturals (starting from 1)
    Check it and return all missing values.

    >>> find_lost_samples(None, [2,3,4,10,15,16,17,18,20])
    [1, 5, 6, 7, 8, 9, 11, 12, 13, 14, 19]

    """
    ch_ind = p_read_mgr.get_param('channels_names').index("SAMPLE_NUMBER")

    last = 0
    lost = []
    #lost += [i for i in range(1,int(last))]
    for samples in p_read_mgr.iter_samples():
        if (samples[ch_ind] - 1) != last:
            lost.append((last+1, samples[ch_ind]))
            print("APPEND: ", str((last+1, samples[ch_ind])))
        last = samples[ch_ind]
    return lost
        
def print_result(l):
    """
    >>> print_result([])
    All samples were written.

    >>> print_result([1,2,3,4,5])
    All but first 5 samples were written.

    >>> print_result([3,4,5,10,11,12,15,16])
    Samples numbers that were NOT written:
    2 - 5
    10 - 12
    15 - 16


    """

    if len(l) == 0:
        print("All samples were written.")
    else:
        for i, v in enumerate(l):
            if i+1 == v:
                continue
            else:
                break
        if len(l[i+1:]) == 0:
            print ("All but first "+str(i+1)+" samples were written.")
        else:
            print ("Samples numbers that were NOT written:")
            #print ('0 - '+str(i+1))
            start = l[0] - 1
            prev = l[0] - 1
            for v in l:
                if v-1 == prev:
                    prev = v
                else:
                    print(str(start)+' - '+str(prev))
                    prev = v
                    start = v
            print(str(start)+' - '+str(prev))            

    
def find_and_print(info_file, data_file, spare_memory=True):
    manager = read_manager.ReadManager(
        info_file,
        data_file,
        None
        )
    l = find_lost_samples(manager, spare_memory=spare_memory)
    print_result(l)
    

if __name__ == "__main__":
    
    if TEST:
        test()
        sys.exit(0)

    if len(sys.argv) >= 3:
        f = {}
        f['info'] = sys.argv[1]
        f['data'] = sys.argv[2]
    else:
        dr = '/media/windows/titanis/bci/projekty/eksperyment_mikolaj/dane_07_12_2010/201/'
        f_name = 'test2-Tue_Dec__7_14_03_55_2010'
        f = {
            'info': os.path.join(dr, f_name+'.obci.info'),
            'data': os.path.join(dr, f_name+'.obci.dat'),
            #'tags':os.path.join(dr, f_name+'.obci.tags')
            }
    try:
        spare_memory = int(sys.argv[3])
    except:
        spare_memory=True

    try:
        saw_name = sys.argv[4]
    except:
        saw_name = "DriverSaw"


    print("ANALYSE: "+str(f))
    manager = read_manager.ReadManager(
        f['info'],
        f['data'],
        None#f['tags']
        )

    l = find_lost_samples(manager, spare_memory=spare_memory, saw_name=saw_name)
    print_result(l)
            
            
        
