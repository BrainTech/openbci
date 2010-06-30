import numpy as np
import matplotlib.pyplot as plt
#from tags.tag_utils import unpack_tag_from_dict 
import experiment_builder.experiment_tag_utils as exp_utils
import signal_prep

def __gen_samples(sine_freqs, len_sec, sample_freq):
    """
    Generate a vector of values of a combination of some sine waves.
    sine_freqs = list of requencies of sine waves
    len_sec = singal length in seconds
    sample_freq = sampling frequency
    """
    # x values
    time_vec = np.arange(0, len_sec, 1.0/sample_freq)
    # result vector
    vals = \
        [sum([(1.0/(x+1)) * np.sin(2 * np.pi * hz * x) for hz in sine_freqs]) \
            for x in time_vec ]
    return vals


def basic_fft_analyse(signal_data, sample_freq, tag=None):
    """
        Apply FFT to signal data and normalise the result.

        signal_data - vector of (real) signal values (one channel)
        sample_freq - sampling rate / s

        Return result_of_fft, vector_of_frequencies
    """
    ft = np.fft.fft(signal_data)
    len_ft = ft.size
    sig_len = len(signal_data)
    
    # Fourier transform is symmetric, ft[0] = DC, 
    # ceil(len_ft/2) - Nyquist freq.
    # Take the first half.
    uniq = ft[0:np.ceil(len_ft/2)]

    # magnitude
    mx = abs(uniq)
    # normalisation (so it is not a function of signal length)
    mx = mx/sig_len
    # energy
    mx = mx ** 2

    # energy correction (we halved the fft result)
    if mx.size % 2:
        # odd length, no Nyquist, first value is unique
        mx[1:] = mx[1:] * 2
    else:
        # even length, first and last values are unique
        mx[1:-1] = mx[1:-1] * 2

    # vector of frequencies, from 0 to sample_freq/2, length = len(mx)
    freqs = [x * (float(sample_freq)/sig_len) for x in range(mx.size)]

    return mx, freqs


"""
d - signal values array, single channel 
window - d contains window * sampling_rate values
sampling_rate - 
numOfFreq - number of stimulation frequencies
returns array of differencies between standard deviations of given freqeuncies and average standard deviation of "other" frequencies
"""

def stat_analyse(d, sampling_rate, tag):

    p_freqs, _fn, window = exp_utils.basic_params(tag)
    freqs = list(p_freqs)
    for i in range(len(freqs)):
        if freqs[i] >= 60:
            freqs[i] = 0
    numOfFreq = len(freqs)
    mul = window

    d2 = abs(np.fft.fft(d))
    d2 = [x**2 for x in d2]
    d2[0] = 0
    d2[1] = 0
    fft_len = len(d2)
    amplitudes = [0] * (numOfFreq * 3)
    otherAmplitudes = numOfFreq * [0]

    freqs_new = (numOfFreq * 3) * [0]
    
    #freqs.sort()
    for i in range(numOfFreq):
        freqs_new[i] = freqs[i]
        freqs_new[i + numOfFreq] = 2 * freqs[i]
        freqs_new[i + (2 * numOfFreq)] = 3 * freqs[i]
        
    freqs = list(freqs_new)


    otherFreqs = (numOfFreq * 3) * [0]
    #print "numOfFreq ", numOfFreq, "len(d2) ", len(d2), " int(freqs[i + (numOfFreq * 2)] * mul) ", \
    #    int(freqs[i + (numOfFreq * 2)] * mul), "freqs ", freqs
    for i in range(numOfFreq):
        otherFreqs[i] = float(freqs[i]) + 0.5

    for i in range(numOfFreq):
        for k in range(2):
            amplitudes[i] = 0
            otherAmplitudes[i] = 0
            if int(freqs[i + numOfFreq*k] * mul) >= fft_len:
                print "INDEX TOO BIG! ", "i: ",i, "k: ", k, "int(freqs[i + numOfFreq*k] * mul)", \
                    int(freqs[i + numOfFreq*k] * mul), " ", fft_len
                continue
            amplitudes[i] += d2[int(freqs[i + numOfFreq*k] * mul)] - \
                            0.5*(d2[int(freqs[i + numOfFreq*k] * mul - 1)] + \
                            d2[int(freqs[i + numOfFreq*k]* mul + 1)])
               
            if int(otherFreqs[i + numOfFreq*k] * mul) >= fft_len:
                print "OTHER INDEX TOO BIG! ", "i: ",i, "k: ", k, "int(otherFreqs[i + numOfFreq*k] * mul)", \
                    int(otherFreqs[i + numOfFreq*k] * mul), " ", fft_len
                continue
            otherAmplitudes[i] += d2[int(otherFreqs[i + numOfFreq*k] * mul)] - \
                                0.5*(d2[int(otherFreqs[i + numOfFreq*k] * mul - 1)] + \
                                 d2[int(otherFreqs[i + numOfFreq*k] * mul + 1)])


    avgAmplitude = 0.0
    avgOtherAmplitude = 0.0

    for i in range(numOfFreq):
        avgAmplitude +=  amplitudes[i]
        avgOtherAmplitude += otherAmplitudes[i]
    avgAmplitude /= float(numOfFreq)
    avgOtherAmplitude /= float(numOfFreq)

    stdAmplitude = 0.0
    stdOtherAmplitude = 0.0        
    diffs = numOfFreq * [0.0]
    otherDiffs = numOfFreq * [0.0]        

    avgs = numOfFreq * [0.0]
    otherAvgs = numOfFreq * [0.0]

    for i in range(numOfFreq):
        avgs[i] = ((avgAmplitude * numOfFreq) - amplitudes[i]) / float(numOfFreq - 1)    
        otherAvgs[i] = ((avgOtherAmplitude * numOfFreq) - otherAmplitudes[i]) / float(numOfFreq - 1)    

    for i in range(numOfFreq):
        diffs[i] = amplitudes[i] - avgs[i]
        otherDiffs[i] = otherAmplitudes[i] - otherAvgs[i]

        
    sumOtherDiffs = 0.0
   
    for i in range(numOfFreq):
        sumOtherDiffs += otherDiffs[i]

    avgOtherDiffs = float(sumOtherDiffs/numOfFreq)

    return [x - avgOtherDiffs for x in diffs], p_freqs


def filtered_spectrum(fftd, freqs, chosen_freqs, len_s):
    """
    Return array of amplitudes for chosen_freqs, instead of all of them.
    fftd - array of transformed data
    freqs - array of frequencies (same length as fftd)
    (fftd, freqs as returned by i.e. basic_fft_analyse())
    chosen_freqs - list of frequencies we want to see on the spectrum
    len_s - length in seconds of the transformed signal
    """
    fil = []
    chosen_freqs.sort()
    for f in chosen_freqs:
        fil.append(fftd[f * len_s])
    return fil, chosen_freqs




def iter_analysed_slices(sig_prep, chan_no, analyse_method=basic_fft_analyse):
    """
    Analyse slices of data using chosen slice_iter and analyse_method.
    Yield analysed data, vector of freqs and start tag.
    tag_mgr - instance of SmartTagManager
    chan_no - signal channel number

    slice_iter - iter_nonbreak_slices, iter_all_exp_slices
    analyse_method - basic_fft_analyse
    """
    sr = sig_prep.get_sampling_rate()
    for data, tag in sig_prep.iter_nonbreak_slices(chan_no):
        fd, freqs = analyse_method(data, sr, tag)
        yield fd, freqs, data, tag
        


def single_freq_test(sig_prep, chan_no):
    """
    Draw summary of an experiment - amplitudes of each frequency on the
    field on which the subject was concentrating.
    """
    tags = []
    single_freqs = []
    amplitudes = []

    for fd, freqs, data, tag in iter_analysed_slices(sig_prep, chan_no,
            analyse_method=basic_fft_analyse):
        tags.append(tag)
        t_freqs, field_no, delay = exp_utils.basic_params(tag)
        single_freq = t_freqs[field_no]
        #TODO get more accurate length from data
        amps, _a = filtered_spectrum(fd, freqs, [single_freq], delay)
        single_freqs.append(single_freq)
        amplitudes.append(amps[0])
    return tags, single_freqs, amplitudes

def multi_freq_stat_test(sig_prep, chan_no):
    """
    Draw diagrams of statistical analysis for each frequency (with all fields blinking).
    """
    diff_chunks = []
    tags = []
    for diffs, ch_freqs, data, tag in iter_analysed_slices(sig_prep, chan_no, 
            analyse_method=stat_analyse):
        tags.append(tag)
        s_freqs = sorted(ch_freqs)
        pos = {}
        for i in range(len(ch_freqs)):
            pos[ch_freqs[i]] = i
        s_diffs = [diffs[pos[s_freqs[i]]] for i in range(len(s_freqs))]
        diff_chunks.append((s_diffs, s_freqs))
    return tags, diff_chunks    






if __name__ == "__main__":
    s_rate = 16
    sins = [2,3,5]
    len_sec = 3

    sig = gen_samples(sins, len_sec, s_rate)
    tr, freqs = np.abs(basic_fft_analyse(sig, s_rate))
    print '%f' % tr[3*len_sec]
 #   plt.plot(freqs, tr)
    chosen = [0.2,2,3,5,6,0.1,4,6.5, 0.8]
    fil, chosen = filtered_spectrum(tr, freqs, chosen, len_sec)
 #   plt.ylabel('Amplitudes')
 #   plt.xlabel('Frequencies')
 #   plt.plot(chosen, fil, 'r+')
#    draw_bars_spectrum(chosen, fil)
#    draw_bars_spectrum(freqs, tr)

#    import plotting
#    plotting.draw_bars_single_freq(chosen, fil, 0.3, 1,2)
#    plt.show()
