#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, time, os.path, pickle
import pylab

from obci.analysis.obci_signal_processing import read_manager
from obci.analysis.csp import modCSPv2 as csp
from obci.analysis.csp import signalParser as sp
from obci.utils import context as ctx

def run(in_file, use_channels, ignore_channels, montage, montage_channels, plot_stats=True,
	context=ctx.get_dummy_context('UgmBlinkingConnection')):
	logger = context['logger']
	mgr = read_manager.ReadManager(
		in_file+'.obci.xml',
		in_file+'.obci.raw',
		in_file+'.obci.tag')
        to_frequency = int(float(mgr.get_param("sampling_frequency")))
	if use_channels is None:
		use_channels = mgr.get_param('channels_names')
	if ignore_channels is not None:
		for i in ignore_channels:
			try:
				use_channels.remove(i)
			except:
				pass

	exp_info = mgr.get_tags('experimentInfo')[0]['desc']
        to_signal = float(exp_info['target_time'])
        freqs = [int(i) for i in exp_info['all_freqs'].split(';')]
	dec_count = int(exp_info['fields_count'])


        data = sp.signalParser(in_file+'.obci')
        train_tags = data.get_train_tags(trial_separator_name='diodes', screen=True)
	logger.info("Run csp with: use_channels: "+str(use_channels)+" motage: "+str(montage)+" montage_channels: "+str(montage_channels))
        q = csp.modCSP(in_file+'.obci', freqs, use_channels, montage, montage_channels)
        q.start_CSP(to_signal, to_frequency, baseline = False, filt='cheby', method = 'regular', train_tags = train_tags)#liczenie CSP
        time = pylab.linspace(1, to_signal, 7)
        t1, t2 = q.time_frequency_selection(to_frequency, train_tags, time=time, frequency_no=dec_count, plt=False)

        logger.info("Got times t1: "+str(t1)+ " and t2: "+str(t2))
	logger.info("Set buffer time:"+str(t2))
        value, mu, sigma, means, stds, out_top, out_bottom = q.count_stats(to_signal, to_frequency, train_tags, plt=plot_stats)#Liczenie statystyk
        logger.info("For freqs: "+str(freqs))
        logger.info("Got means: "+str(means))
        
        pairs = zip(means, freqs)
        pairs.sort(reverse=True)
        logger.info("Sorted: "+str(pairs))
	best = [i[1] for i in pairs]
        best_means = [i[0] for i in pairs]
        logger.info("Best freqs: "+str(best))
        
        logger.info("Finished CSP with stats:")
        logger.info(str(value) + " / " + str(mu) + " / " + str(sigma))
        logger.info("And q:")
        logger.info(str(q))
        
        d = {'value': value,
             'mu': mu,
             'sigma': sigma,
             'q' : q,
	     'freqs':';'.join([str(i) for i in best[:dec_count]]),
	     'all_freqs':';'.join([str(i) for i in best]),
	     'all_means':';'.join([str(i) for i in best_means]),
	     'dec_count':dec_count,
	     'buffer':t2,
	     'use_channels':';'.join(use_channels),
	     'montage':montage,
	     'montage_channels':';'.join(montage_channels),
	     'out_top':out_top,
	     'out_bottom':out_bottom
             }
	return d
