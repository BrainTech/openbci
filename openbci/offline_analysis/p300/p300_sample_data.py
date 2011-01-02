#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
from PyML import *
import os.path      
from offline_analysis.p300 import chain_analysis_offline as my_tools
def mati_files(t):
    if t == 'squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_longer_8trials2'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]
    elif t == 'numbers':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/letters/'
        f2_name = 'p300_128hz_laptop_training_6x6_letter_CATDOGFISHWATERBOWL_longer_12trials'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]
    elif t == 'numbered_squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_10_12_2010/numbered_squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBERS_CATDOGFISHWATERBOWL_longer_8trials'          
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]

def lukasz_files(t):
    if t == 'squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_20_12_2010/squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_ublinkShot150_lukasz'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]
    ######
    # Do dupy te dane
    

def maciek_files(t):
    if t == 'squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_20_12_2010/squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_ublinkShot100_maciek'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]
    elif t == 'numbered_squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_20_12_2010/numbered_squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBER_CATDOGFISHWATERBOWL_ublinkShot100_maciek'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]
        

def aga_files(t):
    if t == 'squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_20_12_2010/squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_square_CATDOGFISHWATERBOWL_ublinkShot100_aga'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]

    elif t == 'numbered_squares':
        dr2 = '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/p300_20_12_2010/numbered_squares/'
        f2_name = 'p300_128hz_laptop_training_6x6_squareNUMBER_CATDOGFISHWATERBOWL_ublinkShot100_aga'
        f2 = {
            'info': os.path.join(dr2, f2_name+'.obci.info'),
            'data': os.path.join(dr2, f2_name+'.obci.dat'),
            'tags':os.path.join(dr2, f2_name+'.obci.arts_free.svarog.tags')
            }
        return [f2]

def bci_competition_files(t):
    dr = '/media/windows/wiedza/bci/mgr/bci_competition_data/'
    if t == 'A':
        files = []
        f_name = 'AAS010R0'
        for i in range(1, 6):
            f = {
                'info': os.path.join(dr, f_name+str(i)+'.mat.csv.obci.info'),
                'data': os.path.join(dr, f_name+str(i)+'.mat.csv.obci.dat'),
                'tags':os.path.join(dr, f_name+str(i)+'.mat.csv.obci.tags')
                }
            files.append(f)
        return files
    elif t == 'B':
        files = []
        f_name = 'AAS011R0'
        for i in range(1, 6):
            f = {
                'info': os.path.join(dr, f_name+str(i)+'.mat.csv.obci.info'),
                'data': os.path.join(dr, f_name+str(i)+'.mat.csv.obci.dat'),
                'tags':os.path.join(dr, f_name+str(i)+'.mat.csv.obci.tags')
                }
            files.append(f)
        return files

def get_files(person, mode):
    if person == 'lukasz':
        return lukasz_files(mode)
    elif person == 'aga':
        return aga_files(mode)
    elif person == 'mati':
        return mati_files(mode)
    elif person == 'maciek':
        return maciek_files(mode)
    elif person == 'bci_competition':
        return bci_competition_files(mode)





def aga_chain(mode, avg_size):
    if mode =='numbered_squares':
        if avg_size == 5:
            ch = [
                my_tools.ReadSignal(files=get_files('aga', 'numbered_squares')),
                my_tools.Montage(montage_type='ears',l_ear_channel='M1', r_ear_channel='M2'),
                my_tools.LeaveChannels(channels=['Pz']),
                my_tools.Filter(**{'wp':0.3, 'ws':0.1, 'gpass': 3.0,
                                   'gstop': 30.0, 'ftype':'cheby2', 'unit':'hz'}),
                my_tools.Filter(**{'wp':15.0, 'ws':25.0, 'gpass': 1.0,
                                   'gstop': 60.0, 'ftype':'ellip', 'unit':'hz'}),
                my_tools.Segment(classes=('target','non-target'),
                                 start_offset=-0.2,
                                 duration=0.6),
                my_tools.Average(bin_selectors=[lambda mgr: mgr['name'] == 'target',
                                                lambda mgr: mgr['name'] == 'non-target'],
                                 bin_names=['target', 'non-target'],
                                 size=avg_size,
                                 baseline=0.0,
                                 strategy='random'),
                my_tools.Downsample(factor=3),
                my_tools.Normalize(norm=2),
                my_tools.PrepareTrainSet(),
                my_tools.SVM(C=10.0,
                             Cmode='classProb',
                             kernel=ker.Linear())
                ]
            return ch
        elif avg_size == 10:
            ch = [
                my_tools.ReadSignal(files=get_files('aga', 'numbered_squares')),
                my_tools.LeaveChannels(channels=['Cz']),
                my_tools.Filter(**{'wp':0.3, 'ws':0.1, 'gpass': 3.0,
                                   'gstop': 30.0, 'ftype':'cheby2', 'unit':'hz'}),
                my_tools.Filter(**{'wp':15.0, 'ws':25.0, 'gpass': 1.0,
                                   'gstop': 60.0, 'ftype':'ellip', 'unit':'hz'}),
                my_tools.Segment(classes=('target','non-target'),
                                 start_offset=-0.1,
                                 duration=0.5),
                my_tools.Average(bin_selectors=[lambda mgr: mgr['name'] == 'target',
                                                lambda mgr: mgr['name'] == 'non-target'],
                                 bin_names=['target', 'non-target'],
                                 size=avg_size,
                                 baseline=0.2,
                                 strategy='random'),
                my_tools.Downsample(factor=3),
                my_tools.Normalize(norm=2),
                my_tools.PrepareTrainSet(),
                my_tools.SVM(C=3.0,
                             Cmode='classProb',
                             kernel=ker.Polynomial(2))
                ]
            return ch

        



def bci_competition_chain(mode, avg_size):
    if mode == 'A':
        if avg_size == 5:
            ch = [
                my_tools.ReadSignal(files=get_files('bci_competition', 'A')),
                my_tools.LeaveChannels(channels=['C3']),
                my_tools.Filter(**{'wp':0.3, 'ws':0.1, 'gpass': 3.0,
                                   'gstop': 30.0, 'ftype':'cheby2', 'unit':'hz'}),
                my_tools.Filter(**{'wp':15.0, 'ws':25.0, 'gpass': 1.0,
                                   'gstop': 60.0, 'ftype':'ellip', 'unit':'hz'}),
                my_tools.Segment(classes=('target','non-target'),
                                 start_offset=0.1,
                                 duration=0.6),
                my_tools.Average(bin_selectors=[lambda mgr: mgr['name'] == 'target',
                                                lambda mgr: mgr['name'] == 'non-target'],
                                 bin_names=['target', 'non-target'],
                                 size=avg_size,
                                 baseline=0.2,
                                 strategy='random'),
                my_tools.Downsample(factor=9),
                my_tools.Normalize(norm=2),
                my_tools.PrepareTrainSet(),
                my_tools.SVM(C=2.0,
                             Cmode='classProb',
                             kernel=ker.Polynomial(2))
                ]
            return ch
        elif avg_size == 10:
            ch = [
                my_tools.ReadSignal(files=get_files('bci_competition', 'A')),
                my_tools.LeaveChannels(channels=['C3']),
                my_tools.Filter(**{'wp':0.3, 'ws':0.1, 'gpass': 3.0,
                                   'gstop': 30.0, 'ftype':'cheby2', 'unit':'hz'}),
                my_tools.Filter(**{'wp':15.0, 'ws':25.0, 'gpass': 1.0,
                                   'gstop': 60.0, 'ftype':'ellip', 'unit':'hz'}),
                my_tools.Segment(classes=('target','non-target'),
                                 start_offset=0.0,
                                 duration=0.5),
                my_tools.Average(bin_selectors=[lambda mgr: mgr['name'] == 'target',
                                                lambda mgr: mgr['name'] == 'non-target'],
                                 bin_names=['target', 'non-target'],
                                 size=avg_size,
                                 baseline=0.0,
                                 strategy='random'),
                my_tools.Downsample(factor=5),
                my_tools.Normalize(norm=2),
                my_tools.PrepareTrainSet(),
                my_tools.SVM(C=0.1,
                             Cmode='classProb',
                             kernel=ker.Gaussian(15))
                ]
            return ch



def get_chain(person, mode, avg_size):
    if person == 'lukasz':
        return lukasz_chain(mode, avg_size)
    elif person == 'aga':
        return aga_chain(mode, avg_size)
    elif person == 'mati':
        return mati_chain(mode, avg_size)
    elif person == 'maciek':
        return maciek_chain(mode, avg_size)
    elif person == 'bci_competition':
        return bci_competition_chain(mode, avg_size)
    
