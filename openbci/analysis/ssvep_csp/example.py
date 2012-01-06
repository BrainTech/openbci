#!/usr/bin/env python
#-*- coding: utf-8 -*-

import modCSPv2 as csp
import ssvep_bci_analysis as sba
import signalParser as sp
#############
#KALIBRACJA
file_name = 'maciek3'#prefiks pliku konfiguracyjnego
to_signal = 4#liczba sekund stymulacji
to_frequency = 128#Częstotliwość do której będziemy downsamplować; lub częstotliwość próbkowania
data = sp.signalParser(file_name)#Wymaga 3 plików .raw, .xml i .tag o danym prefiksie
train_tags = data.get_train_tags(tag_filter=('field','4'))#Tak na przykład dla 4 częstotliwości
freqs = [15, 17, 19, 25]#lista częstotliwości
channels = ['O1','O2','T5','P3','Pz','P4','T6']#nazwa kanałów usznych to A1 i A2; jeśli nie to trzeba zmienić
                                                #modCSPv2 w funkcji prep_signal
q = csp.modCSP(file_name, freqs, channels)
q.start_CSP(signal_time, to_frequency, baseline = False, filt='cheby', method = 'regular', train_tags = train_tags)#liczenie CSP
value, mu, sigma = q.count_stats(signal_time, to_freq, train_tags)#Liczenie statystyk
#Dalej do analizy online potrzebne będzie q.P, value, mu i sigma
#Koniec kalibracji
##############

#############
#Analiza online
#Mamy sygnał jako macierz o odpowiedniej liczbie kanałów i zadanej długości
#Najpierw trzeba go przefiltrować przez CSP
csp_sig = np.dot(q.P[:,0], signal)#dostajemy jeden kanał o zadanej długości
csp_sig -= csp_sig.mean()#normujemy
csp_sig /= np.sqrt(np.sum(csp_sig*csp_sig))#normujemy
#detekcja
result = sba._analyze(csp_signal, to_frequency, freqs, value, mu, sigma)