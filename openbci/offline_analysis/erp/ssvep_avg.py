#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scipy
import pylab
import sys
sys.path.insert(1, '../../../')
sys.path.insert(1, '../../../openbci/')

def test_generate_data():
    Fs = 128  # the sampling frequency
    POINTS = 1024.0
    t = pylab.array([i/POINTS for i in range(int(POINTS))])
    s1 = pylab.sin(2*pylab.pi*15*t*POINTS/Fs)*2
    s2 = pylab.sin(2*pylab.pi*30*t*POINTS/Fs) #zeros(len(t))

    s3 = pylab.sin(2*pylab.pi*10*t*POINTS/Fs)*2
    s4 = pylab.sin(2*pylab.pi*20*t*POINTS/Fs) #zeros(len(t))
    

    nse = pylab.randn(len(t))
    x1 = s1 + s2 + nse # the signal
    x2 = s3 + s4 + nse # the signal
    return pylab.array([x1, x2])

def test_norm_data():
    Fs = 128  # the sampling frequency
    POINTS = 1024.0
    t = pylab.array([i/POINTS for i in range(int(POINTS))])
    s1 = pylab.sin(2*pylab.pi*15*t*POINTS/Fs)*2/1.1
    s2 = pylab.sin(2*pylab.pi*30*t*POINTS/Fs)/2 #zeros(len(t))

    s3 = pylab.sin(2*pylab.pi*10*t*POINTS/Fs)*2/1.1
    s4 = pylab.sin(2*pylab.pi*20*t*POINTS/Fs)/2 #zeros(len(t))
    

    nse = pylab.randn(len(t))/2
    x1 = s1 + s2 + nse # the signal
    x2 = s3 + s4 + nse # the signal
    return pylab.array([x1, x2])

    
def test_plot_avs(avs, freqs):
    for j in range(len(avs)):
        pylab.subplot(len(avs)/2, 2, j+1)
        pylab.plot(freqs, avs[j])
    pylab.show()
    
def get_normalised_avgs(samples_source,
                        norm_array,
                        norm_type,
                        NFFT,
                        Fs,
                        noverlap,
                        window=None):
    """Return a two dimensional array of averaged signals

    >>> from openbci.offline_analysis.obci_signal_processing.signal import read_data_source as s

    >>> ss1 = [s.MemoryDataSource(test_generate_data())]

    >>> avs1,freqs1 = get_normalised_avgs(ss1, None, 'nic', 128, 128, 127)


    >>> ssx = [s.MemoryDataSource(test_norm_data())]

    >>> avsx,freqsx = get_normalised_avgs(ssx, None, 'nic', 128, 128, 127)


    >>> ss = [s.MemoryDataSource(test_generate_data())]

    >>> avs,freqs = get_normalised_avgs(ss, avsx, 'divide', 128, 128, 127)

    >>> test_plot_avs(pylab.array([avs1[0], avs1[1], avsx[0], avsx[1], avs[0], avs[1]]), freqs)

    """
    #l_num_of_channels = p_st_manager.num_of_channels
    if window is None:
        window = pylab.blackman(NFFT)
    i = 0
    ret_freqs = None
    ret_avgs = None
    for i_source in samples_source:
        for j, ch in enumerate(i_source.get_samples()):
            Pxx, freqs, bins, im = pylab.specgram(ch, NFFT=NFFT, Fs=Fs, noverlap=noverlap, window=window)
            if i == 0 and j == 0:
                ret_freqs = freqs                
                ret_avgs = pylab.zeros((len(i_source.get_samples()), len(freqs)))
            ret_avgs[j, :] = ret_avgs[j, :] + pylab.array([pylab.average(a) for a in Pxx])
        i += 1

    assert(i > 0)
    # Sums are computed, now lets divide, so that we get an average
    for j in range(len(ret_avgs)):
        ret_avgs[j, :] = ret_avgs[j,:]/float(i)
        if norm_type == 'substract':
            ret_avgs[j, :] = ret_avgs[j, :] - norm_array[j, :]
        elif norm_type == 'divide':
            ret_avgs[j, :] = (ret_avgs[j, :] - norm_array[j, :]) / ret_avgs[j, :]            
    return ret_avgs, ret_freqs

TEST = True
def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")


if __name__ == '__main__':
    if TEST:
        test()
        sys.exit(0)
