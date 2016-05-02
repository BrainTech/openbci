#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import time
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft,fft,fftfreq,fftshift

#Ania:wyciagnelam definicje funkcji zeby byla globalna nie tylko dostepna z wnetrza funkcji run
def widmo_mocy(s, fs):
    S = fft(s)/np.sqrt(len(s))
    S_moc = S*S.conj()
    S_moc = S_moc.real
    F = fftfreq(len(s), 1/fs)
    return (fftshift(F),fftshift(S_moc))


def run(data, fs, nazwy_kanalow, L_buffer):
    print "Analysis run..."
    
    config = {'srednie_widmo': 0, 
			  'os_czestosci': 1,
              'odch_std': 2}
    #Ania:zakomentowałam ten czas bo on tylko spowalnia;)
    #time.sleep(10)
    
    N_kanalow = len(nazwy_kanalow)-4 #odjac dwie pily i elektrody uszne
    
    data = data[:-2] - (data[-3]+data[-4])/2. #montaz jezeli dwa ostatnie sygnaly sa elektrodami usznymi
    
    dl_odcinka = L_buffer*fs #wartosc w probkach
    
    ilosc_powtorzen = len(data[0])/float(dl_odcinka) #ilosc odcinkow mieszczacych sie w sygnale
    pociete_dane = np.zeros((N_kanalow, dl_odcinka, ilosc_powtorzen)) #kanal  sygnal  powtorzenie
    

    for j in xrange(N_kanalow):
		for i in xrange(int(ilosc_powtorzen)):
			pociete_dane[j,:,i]= data[j,i*dl_odcinka : (i+1)* dl_odcinka]

    
    #obliczanie widma dla kazdego powtorzenia        
    widmo_po_odcinkach = np.zeros([N_kanalow, dl_odcinka, ilosc_powtorzen]) #kanal x widmo x powtorzenie
    
 
    for j in xrange(int(N_kanalow)):  #petla po kanalach
		for i in xrange(int(ilosc_powtorzen)): #petla po powtorzeniach
			os_czestosci, widmo_po_odcinkach[j, :, i] = widmo_mocy(pociete_dane[j,:,i], fs)

    
    #usrednianie powtorzen
    widmo_sr = np.mean(widmo_po_odcinkach, axis=2) #kanal x srednie widmo 
    od_std = np.std(widmo_po_odcinkach, axis=2) #czy to jest poprawnie? 
    
    msc_30Hz =  np.where(os_czestosci==30.)[0][0]
    msc_2Hz =  np.where(os_czestosci==2.)[0][0]

    #wycinanie przedzialow
    os_x = os_czestosci[msc_2Hz:msc_30Hz+1]
    widmo = widmo_sr[:, msc_2Hz:msc_30Hz+1]#korytarze ufnosci
    od_std = od_std[:, msc_2Hz:msc_30Hz+1]
    
    #wykres z korytarzami
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.plot(os_x,widmo_sr_up[0])
    ax.plot(os_x,widmo_sr_down[0])
    plt.show()
    
    '''
    #wykres z korytarzami
    f = plt.figure()
    ax = f.add_subplot(111)
    plt.errorbar(os_x, widmo[0], od_std[0], linestyle='None', marker='^')
    plt.show()'''

    #Ania: w rysowaniu brakowalo definicji czym jest ax;)
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.plot(os_x,widmo[0])
    plt.show()
        
    print "Analysis finish..."
    return config

#Ania: dopisalam funkcje ponizsze i teraz nie musisz przez obci uruchamiac tej funkcji zeby testowac tylko ten plit robisz w konsoli python NAZWA_PLIKU, to rozwiazanie bedzie szybsze do prototypowania;) 
if __name__ == '__main__':
    run(np.random.rand(8, 2*256*10), 256, ['a']*8, 2)
