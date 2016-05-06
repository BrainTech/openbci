#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import pylab as py
import numpy as np
from numpy.fft import  fft, fftfreq, fftshift

def run(data, config, channel_names, first_sample_timestampm, fs):
    print "Analysis run..."
    # montaz, odciecie trendu, widmo met Welcha
    config = {'param1': 0, 
              'param2': 1}
    time.sleep(10)
    
    N = data.shape[1]
    NW = 3
    N_s = N/8

    okno = np.hamming(N_s)
    #okno = np.blackman(N)

    #welch
    #okno2 = np.hamming(N_s)
    #okno2 = np.blackman(N_s)

    sygnal = montaz(data, channel_names) #program wyk na sygnale zmontowanym

    # Wywolywanie widma mocy met. Welcha i met. multitaper dla wszystkich kanalow #
    wynikiWelch = np.zeros((len(data), N_s))
    print "wynikiWelch.shape: ", wynikiWelch.shape
    wynikiMulti = np.zeros((len(channel_names), fs/2.))
    for i in range(0,sygnal.shape[0]):
        print "wynikiWelch[i,:].shape: ", wynikiWelch[i,:].shape
        a = pwelch(sygnal[i], okno, 1, fs)
        print "pwelch(sygnal[i], okno2, 1, fs)[1]: ", a[0].shape
        print "pwelch(sygnal[i], okno2, 1, fs)[2]: ", a[1].shape
        (wynikiWelch[i,:], F_welch) = pwelch(sygnal[i], okno, 1, fs)
    #for j in range(0,sygnal.shape[0]):
    #    wynikiMulti[j,:], F_multi = multitaper(sygnal[j], NW, fs)

    # Plotowanie #
    py.subplot(2,1,1)
    py.plot(F_welch, wynikiWelch[0]) 
    py.title('Widmo mocy metoda Welcha')

    #py.subplot(2,1,2)
    #py.plot(wynikiMulti, F_multi) 
    #py.title('Widmo mocy metoda multitaper')
    py.show()
    
    print "Analysis finish..."
    return config

# Montaz dwubiegunowy uszny #
def montaz(data, channel_names):
    sygnalZmon = np.zeros(data.shape)
    ucho1 = len(channel_names)-3
    ucho2 = len(channel_names)-4
    numberOfChannels = len(channel_names)
    for i in range(0,numberOfChannels-4):
	sygnalZmon[i,:] = data[i,:] - (data[ucho1,:] + data[ucho2,:])/2.
    return sygnalZmon

'''Algorytm Welcha:
1. Sygnał x o długości N jest dzielony na segmenty, każdy o długości N_s. Odcinki mogą na siebie zachodzić na N_z punktów. Czyli są względem siebie przesunięte o N_p = N_s-N_z. 
2. Z każdego segmentu liczony jest okienkowany periodogram
3. Periodogramy są sumowane
4. Wynik dzielony jest przez efektywne wykorzystanie każdego kawałka sygnału w estymacie: K_eff = dlugosc_okna * ilosc_okien / dlugosc_sygnalu''' 

def periodogram(data, okno, fs):
    s = data*okno
    N_fft = len(s)
    S = fft(s,N_fft)#/np.sqrt(N_fft)
    P = S*S.conj()/np.sum(okno**2)
    
    P = P.real
    F = fftfreq(N_fft, 1/fs)
    return fftshift(P),fftshift(F)

def pwelch(data, okno, przesuniecie, fs):
    N = len(data)
    N_s = len(okno)
    
    start_fragmentow = np.arange(0,N-N_s+1,przesuniecie)
    ile_fragmentow = len(start_fragmentow)
    ile_przekrycia = N_s*ile_fragmentow/float(N)
    P_sredni = np.zeros(N_s)
    for i in range(ile_fragmentow):
        s_fragment = data[start_fragmentow[i]:start_fragmentow[i]+N_s]
        P, F = periodogram(s_fragment,okno,fs)
        P_sredni += P
    return P_sredni/ile_przekrycia,F


'''
Algorytm multitaper:
1. Obliczyc maksymalną liczbę okienek:K = 2*NW-1
2. Obliczyc długość sygnału
3. Wygenerowac serię okienek dpss
4. Dla każdego z otrzymanych okienek obliczyc widmo mocy iloczynu tego okienka i sygnału. 
Dla i-tego okienka będzie to: Si = np.abs(fft(s*w.dpssarray[i]))**2
5. Uśrednic widma otrzymane dla wszystkich okienek
6. Wygenerowac oś częstości: fftfreq
'''

def multitaper(data, NW, fs):
    '''estymacja widma w oparciu o  metodę Multitaper 
    x - sygnał
    N -ilość punktów okna
    NW - iloczyn długości okna w czasie i szerokości w częstości
    K - ilość okien
    funkcja zwraca estymatę mocy widmowej
    '''
    K = 2*NW-1
    N = len(data)
    w = dpss.gendpss(N,NW,K)
    S=np.zeros(N)
    for i in range(K):
        Si = np.abs(fft(data*w.dpssarray[i]))**2
        S[:] += Si.real
    S = S/K
    F = fftfreq(N,1.0/fs)
    return (fftshift(S),fftshift(F))

"""
N = len(data)
NW = 3
N_s = N/8

okno = np.hamming(N)
#okno = np.blackman(N)

#welch
okno2 = np.hamming(N_s)
#okno2 = np.blackman(N_s)

sygnal = montaz(data) #program wyk na sygnale zmontowanym

# Wywolywanie widma mocy met. Welcha i met. multitaper dla wszystkich kanalow #
wynikiWelch = np.zeros(len(channel_names), fs/2.)
wynikiMulti = np.zeros(len(channel_names), fs/2.)
for i in range(0,sygnal.shape[0]):
        wynikiWelch[i,:], F_welch = pwelch(sygnal[i], okno2, 1, fs)
for j in range(0,sygnal.shape[0]):
        wynikiMulti[j,:], F_multi = multitaper(sygnal[j], NW, fs)

# Plotowanie #
py.subplot(2,1,1)
py.plot(wynikiWelch, F_welch) 
py.title('Widmo mocy metoda Welcha')

py.subplot(2,1,2)
py.plot(wynikiMulti, F_multi) 
py.title('Widmo mocy metoda multitaper')
py.show()

'''py.subplot(2,1,2)        
(P,F) = pwelch(sygnal,okno2,N_s/10,fs)
py.plot(F,P)
py.title('periodogram Welcha'+' energia: '+ str(np.sum(P)))
py.show()'''

"""
