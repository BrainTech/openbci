#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
# About script:
#       The main purpose of this script is to resample the data from uneven
#   sampling to the exact value of sampling rate.

from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import matplotlib.pyplot as plt
import numpy as np

def get_file_list(catalogue):
    """
    :return: List of not resampled files from catalogue.
    """
    checker = []
    file_list = []
    for paths, subcatalogs, files in walk(r'./'+catalogue):
        for file in files:
            if 'incomplete' not in paths and 'obci' in file:
                file = cut_extension(file)
                if file not in checker and 'resampled' not in file:
                    file_list.append(path.join(paths, file))
                    checker.append(file)
    return file_list

def cut_extension(file):
    """
    :param file: Name of the file.
    :return: Name of the file without extension.
    """
    string = file[0]
    for char in range(1, len(file)):
        if file[char] == '.':
            return string
        else:
            string += file[char]

def get_read_manager(file_name):
    """
    :param file_name: File without extension.
    :return: WBBReadManager object with channels x and y.
    """
    w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       file_name+'.obci.tag')
    w.get_x()
    w.get_y()
    return w

def resample(w, file, sampling_rate):
    """
    Main part of the file. Method of the resampling is generally as follows:
     - creation of three arrays, for new timestamps, for new x and new y,
     - creation of bins for each new sample,
     - if old samples have higher frequency, they goes to the same bin and
        new sample is counted as mean of the old ones,
     - if old samples have lower frequency (undesirable situation), new sample
        is equal to the previous one.
    :param w:
    :param file:
    :return:
    """
    old_x = w.get_x()
    old_y = w.get_y()
    time_new = np.arange(0, w.get_timestamps()[-1], 1./sampling_rate)
    new_x = np.zeros((len(time_new)))
    new_y = np.zeros((len(time_new)))
    a, b, c = plt.hist(w.get_timestamps(), bins=len(time_new), range=(0, time_new[-1]))
    print(a)
    suma_wzietych=0

    for ind, liczba in enumerate(a):
        if old_x[suma_wzietych:suma_wzietych+liczba].any():
            new_x[ind] = np.mean(old_x[suma_wzietych:suma_wzietych+liczba])
            new_y[ind] = np.mean(old_y[suma_wzietych:suma_wzietych+liczba])
        else:
            new_x[ind] = new_x[ind-1]
            new_y[ind] = new_y[ind-1]
        suma_wzietych += liczba
    wbb = w
    print(new_y)
    wbb.mgr.set_samples(np.array([new_x, new_y, time_new]), ['x', 'y', 'TSS'])
    wbb.mgr.set_param('sampling_frequency', sampling_rate)
    counter = 0

    for i in range(0, len(file)):
        if counter == 4:
            break
        if file[i] == '/':
            counter += 1
    new_file_name = file[i:]+'_resampled'
    # set your own new_file_name

    wbb.mgr.save_to_file(file[0:i], new_file_name)

if __name__ == '__main__':

    # parameters of resampling:
    catalogue = 'dual_data'
    sampling_rate = 33.5

    file_list = get_file_list(catalogue)
    for file in file_list:
        w = get_read_manager(file)
        resample(w, file, sampling_rate)