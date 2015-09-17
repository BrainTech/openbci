#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from __future__ import print_function, division
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *
import numpy as np
import pandas as pd

def velocity(wbb_mgr, x, y):
    return wii_mean_velocity(wbb_mgr, x, y)

def distance(x, y):
    x = abs(x - np.mean(x))
    y = abs(y - np.mean(y))
    return np.mean(np.sqrt((x*x)+(y*y))), np.mean(x), np.mean(y)

def marker(name, wbb, x, y, axis='xy'):
    """
    :param name: Name of the marker: COP, elipsa, predkosc, odleglosc.
    :param wbb: ReadManager object.
    :param x: x samples.
    :param y: y samples.
    :param axis: Specifies if marker is counted for only one axis ('x', 'y')
                 or for both axis ('xy', default value).
    :return: Marker value.
    """
    if name == 'COP':
        return wii_COP_path(wbb_mgr, x, y, plot=False)[0]
    elif name == 'elipsa':
        return wii_confidence_ellipse_area(x, y)
    elif name == 'predkosc':
        if axis == 'xy':
            return velocity(wbb, x, y)[0]
        elif axis == 'x':
            return velocity(wbb, x, y)[1]
        elif axis == 'y':
            return velocity(wbb, x, y)[2]
        else:
            print("Wrong axis.")
            return None
    elif name == 'odleglosc':
        if axis == 'xy':
            return distance(x, y)[0]
        elif axis == 'x':
            return distance(x, y)[1]
        elif axis == 'y':
            return distance(x, y)[2]
        else:
            print("Wrong axis.")
            return None
    else:
        print("Unknown marker.")
        return None

def romberg(marker, base):
    """
    :param marker: Value of marker for any task.
    :param base: Value of marker for basic task, as free standing.
    :return: Value of specified romberg parameter.
    """
    return base/marker

def poly(pre, post):
    """
    :param pre: Pretest data.
    :param post: Posttest data.
    :return: Value measuring diffrence between pretest and posttest, given
             in percents.
    """
    return ((pre - post)/(post + pre)) * 100

def basic_stats(data, group):
    """
    :param data: DataFrame with one marker values
    :param group: Indicates group (each group has its own bar on chart)
    :return: Basic stats for each group: mean value, standard deviation.
    """
    tests = ['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze']
    prefixes = ['_pre', '_post']

    result_stats = pd.DataFrame()
    result_stats['stat_name'] = pd.Series(['mean', 'std_dev'])

    for test in tests:
        for prefix in prefixes:
            if marker == 'romberg' and test == 'stanie':
                continue
            test_list = data[data['session_type'] == group][test+prefix].tolist()
            test_list = [x for x in test_list if x != ' ']
            test_list = to_float(test_list)
            mean_value = sum(test_list)/len(test_list)
            std_dev = np.std(test_list)
            result_stats['{}{}'.format(test, prefix)] \
                = pd.Series([mean_value, std_dev])
    return result_stats

def to_float(list):
    """
    :param list: List of elements .
    :return: List of float elements.
    """
    result = []
    for elem in list:
        elem = float(elem)
        result.append(elem)
    return result

