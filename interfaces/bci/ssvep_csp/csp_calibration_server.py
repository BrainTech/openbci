#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>


from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

import sys, time, os.path, pickle
import settings, variables_pb2
import pylab

from openbci.analysis import analysis_logging as logger
LOGGER = logger.get_logger("csp_server", 'info')

import modCSPv2 as csp
import signalParser as sp


class CSP(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(CSP, self).__init__(addresses=addresses, 
                                          type=peers.ANALYSIS)

        l_f_name =  self.conn.query(message = "SaveFileName", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message
        l_f_dir = self.conn.query(message = "SaveFilePath", 
                                   type = types.DICT_GET_REQUEST_MESSAGE, 
                                   timeout = 1).message
        l_f_dir = os.path.normpath(l_f_dir)


        file_name = os.path.normpath(os.path.join(
               l_f_dir, l_f_name))

        to_signal = 4#liczba sekund stymulacji
        to_frequency = 128#Częstotliwość do której będziemy downsamplować; lub częstotliwość próbkowania
        data = sp.signalParser(file_name+'.obci')#Wymaga 3 plików .raw, .xml i .tag o danym prefiksie
        train_tags = data.get_train_tags(tag_filter=('field', '8'))#888 ('field','4'))#Tak na przykład dla 4 częstotliwości
        #freqs = [13, 15, 17, 19, 21, 23, 14, 16] 
        #freqs = [30, 32, 34, 36, 40, 42, 44, 46] 
        #freqs = [36, 45, 39, 33, 42, 48, 51, 30]
        #freqs = [41, 53, 35, 32, 44, 47, 55, 38]
        #freqs = [30, 31, 32, 33, 34, 35, 36, 37]#, 38, 39, 40, 41,

        #freqs = [30, 31, 32, 33, 34, 35,
        #         36, 37, 38, 39, 40, 41,
        #         42, 43, 44, 45]#[32, 35, 38, 41, 44, 47, 53, 55]
        freqs = [13, 14, 15, 16, 
              17, 18, 19, 20]

        #freqs = [13, 15, 17, 19, 21, 23,
        #         25, 27, 29, 31, 33, 35,
        #         37, 39, 41, 43]

        
        #freqs = [15, 17, 19, 25]#lista częstotliwości
        channels = ['O1','O2','T5','P3','Pz','P4','T6']#nazwa kanałów usznych to A1 i A2; jeśli nie to trzeba zmienić
                                                #modCSPv2 w funkcji prep_signal

        q = csp.modCSP(file_name+'.obci', freqs, channels)
        q.start_CSP(to_signal, to_frequency, baseline = False, filt='cheby', method = 'regular', train_tags = train_tags)#liczenie CSP
        time = pylab.linspace(1, to_signal, 7)
        t1, t2 = q.time_frequency_selection(to_frequency, train_tags, time=time, frequency_no=8, plt=False)

        LOGGER.info("Got times t1: "+str(t1)+ " and t2: "+str(t2))
        
        value, mu, sigma, means, stds = q.count_stats(to_signal, to_frequency, train_tags, plt=True)#Liczenie statystyk

        LOGGER.info("For freqs: "+str(freqs))
        LOGGER.info("Got means: "+str(means))
        
        pairs = zip(means, freqs)
        pairs.sort(reverse=True)
        LOGGER.info("Sorted: "+str(pairs))
        LOGGER.info("Best freqs: "+str([i[1] for i in pairs]))
        
        LOGGER.info("Finished CSP with stats:")
        LOGGER.info(str(value) + " / " + str(mu) + " / " + str(sigma))
        LOGGER.info("And q:")
        LOGGER.info(str(q))
        
        csp_file = file_name+'.csp'
        f = open(csp_file, 'w')
        d = {'value': value,
             'mu': mu,
             'sigma': sigma,
             'q' : q
             }
        pickle.dump(d, f)
        f.close()
        sys.exit(0)


if __name__ == "__main__":
    CSP(settings.MULTIPLEXER_ADDRESSES).loop()


        
