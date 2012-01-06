#!/usr/bin/env python
#-*- coding: utf-8 -*-
import numpy as np
from scipy.signal import hamming

def _analyze_old(data, fs, freqs, harm=2, other_freqs=1):
    """Function to analyze SSVEP
    
    This function performs analysis an classification of SSVEP in signal data
    For larger description of used method see [1]
    Parameters:
    ==========
    data : 1darray
        a vector of data to analyze
    fs : int
        sampling frequency
    freqs : list
        a list of frequencies to analyze
    harm [= 2] : int
        number of harmonics to consider
    other_freqs [= 2]: int
        if is int, the frequencies against which null hypoythesis will be tested
        are specified as other_freqs next bin in fft spectrum
    
    Returns:
    ========
    f : float
        detected frequency
    Z : float
        a Z-score of selected frequency
    p_value : float
        the p value of selected frequency
    
    References:
    ===========
    [1] User-centered design of Brain Computer Interfaces: OpenBCI.pl and BCI
    Appliance; Durka, Piotr J. et al.
    """
    Fs = float(fs)
    if harm * max(freqs) >= Fs / 2:
        raise ValueError('Exceeding Nyquist frequency. Lowering number of harmonics might help.')
    N = data.size
    NS = len(freqs)
    window = hamming(N)
    fft = np.abs(np.fft.fft(data))**2 / N
    fft *= window
    Q = np.zeros(NS)
    other = np.zeros(NS)
    if not type(other_freqs) is int:
        raise ValueError('The other_freqs must be an int!')
    if max(other) * harm >= Fs/2:
        raise ValueError('Exceeding Nyquist frequency. Lowering number of harmonics might help.')
    Q_test = np.zeros(NS)
    df = N / Fs
    for i, f in enumerate(freqs):
        for j in xrange(1, harm + 1):
            idx = int(f * j * df)
            #idx2 = int(other[i] * j * df)
            idx2 = idx + other_freqs
            Q[i] += 2 * fft[idx] - fft[idx - 1] - fft[idx + 1]
            Q_test[i] += 2 * fft[idx2] - fft[idx2 - 1] - fft[idx2 + 1]
    Q /= float(harm)
    Q_test /= float(harm)
    sumQ = np.sum(Q) / (NS - 1)
    sumQ_test = np.sum(Q_test) / (NS - 1)
    R = [qi * NS - sumQ for qi in Q]
    R_test = [qi * NS - sumQ_test for qi in Q_test]
    max_idx = R.index(max(R))
    selectedFrq = freqs[max_idx]
    meanTest = np.mean(R_test)
    stdTest = np.std(R_test)
    Z = (R[max_idx] - meanTest) / stdTest
    p_value = np.exp(-Z ** 2 / 2.0)/np.sqrt(2*np.pi)
    return selectedFrq, Z, p_value

def _analyze(signal, fs, freqs, value, mu, sigma):
    """This function performs classification based on correlations
    
    Parameters:
    ===========
    signal : 1darray
        signal to be analyzed. It is one dimensional, so probably needs to be
        spatialy filtered first.
    fs : int
        sampling frequency in Hz
    freqs : list
        frequencies to be detected in signal
    value : float
        a treshold value, above which detection will be positive
    mu : float
        a mean value of test distribution (for Z-scoring)
    sigma : float
        a standard deviation of test distribution (for Z-scoring)
    
    Returns:
    ========
    result : float or 0
        if there was successful detection, selected frequency will be returned.
        In other case, 0 is returned.
    """
    N = len(signal)
    T = N / float(fs)
    t_vec = np.linspace(0, T, N)
    max_lag = int(0.1 * fs)
    sig = signal /  np.sqrt(np.sum(signal * signal))
    result = 0
    mx_old = 0
    for f in freqs:
        sin = np.sin(2*np.pi*t_vec*f)
        sin /= np.sqrt(np.sum(sin * sin))
        xcor = np.correlate(sig, sin, 'full')[N - 1 - max_lag:N+max_lag]
        mx = (np.max(xcor) - mu)/sigma
        if mx > value:
            if mx > mx_old:
                result = f
                mx_old = mx
    return result