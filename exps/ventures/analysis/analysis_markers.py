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
import analysis_user_file
import analysis_helper
import numpy as np
import pandas as pd
from scipy import signal

def velocity(wbb_mgr, x, y):
    return wii_mean_velocity(wbb_mgr, x, y)

def distance(x, y):
    x = abs(x - np.mean(x))
    y = abs(y - np.mean(y))
    return np.mean(np.sqrt((x*x)+(y*y))), np.mean(x), np.mean(y)

def get_marker(name, wbb, x, y, axis='xy'):
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
        return wii_COP_path(wbb, x, y, plot=False)[0]
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
            if get_marker == 'romberg' and test == 'stanie':
                continue
            test_list = data[data['session_type'] == group][test+prefix].tolist()
            test_list = [x for x in test_list if x != ' ']
            test_list = to_float(test_list)
            mean_value = sum(test_list)/len(test_list)
            std_dev = np.std(test_list)
            result_stats['{}{}'.format(test, prefix)] \
                = pd.Series([mean_value, std_dev])
    return result_stats

def count_area(start, stop, data):
    area = []
    for i in range(start, stop):
        if data[i].any():
            x = data[i][0]*22.5
            y = data[i][1]*13
            area.append(wii_confidence_ellipse_area(x, y))
    return area

def filter_signal(x):
    b, a = signal.butter(2, 0.5/(33.5/2), 'high')
    return signal.filtfilt(b, a, x)

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

def get_group_data(marker, test, group):
    """
    :params: defined in main part of the script, indicate files with input
        data.
    :return: lists with values of marker in test for one group (one for
        pretest, one for posttest).
    """
    file_path = 'data/markers_' + marker + '.csv'
    data = pd.read_csv(file_path, index_col=0, dtype='str')

    test_pre = test + '_pre'
    test_post = test + '_post'
    pre_str = data[data['session_type'] == group][test_pre].values
    post_str = data[data['session_type'] == group][test_post].values

    pre = []
    post = []
    for elem in pre_str:
        if elem is not ' ':
            elem = float(elem)
            pre.append(elem)
    for elem in post_str:
        if elem is not ' ':
            elem = float(elem)
            post.append(elem)

    return pre, post

def average_difference_sign(pre, post):
    """
    Counts direction of change.
    """
    sum = 0
    for i in range(0, len(pre)):
        sum += post[i] - pre[i]
    if sum/len(pre) == 0:
        return 0
    elif sum/len(pre) < 0:
        return '-'
    else:
        return '+'

def get_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype, users_data):
    """
    Returns the following markers in one DataFrame row:
    - COP
    - ellipse 95% area
    - velocity
    """
    user_data_elipse = pd.DataFrame()
    user_data = pd.DataFrame()
    user_data_velocity = pd.DataFrame()

    task_pre, task_oczy_pre, task_bacznosc_pre, task_gabka_pre, \
        task_poznawcze_pre = analysis_user_file.get_data(wbb_mgr_pre)
    task_post, task_oczy_post, task_bacznosc_post, task_gabka_post, \
        task_poznawcze_post = analysis_user_file.get_data(wbb_mgr_post)

    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        user_data[name] = pd.Series([t])
        user_data_elipse[name] = pd.Series([t])
        user_data_velocity[name] = pd.Series([t])

    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_pre, task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):

        x, y = analysis_helper.remove_baseline(t)
        if analysis_user_file.user_task_checker(username, name, users_data):
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_marker('COP', name, x, y)])
            user_data_elipse['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_marker('elipsa', name, x, y)])
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_marker('predkosc', name, x, y)])
        else:
            user_data['{}_{}'.format(name, 'pre')] = pd.Series([' '])
            user_data_elipse['{}_{}'.format(name, 'pre')] = pd.Series([' '])
            user_data_velocity['{}_{}'.format(name, 'pre')] = pd.Series([' '])

    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):

        x, y = analysis_helper.remove_baseline(t)
        if analysis_user_file.user_task_checker(username, name, users_data):
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series([get_marker('COP', name, x, y)])
            user_data_elipse['{}_{}'.format(name, 'post')] \
                = pd.Series([get_marker('elipsa', name, x, y)])
            user_data_velocity['{}_{}'.format(name, 'post')] \
                = pd.Series([get_marker('predkosc', name, x, y)])
        else:
            user_data['{}_{}'.format(name, 'post')] = pd.Series([' '])
            user_data_elipse['{}_{}'.format(name, 'post')] = pd.Series([' '])
            user_data_velocity['{}_{}'.format(name, 'post')] = pd.Series([' '])

    return user_data, user_data_elipse, user_data_velocity

def get_romberg(wbb_mgr_pre, wbb_mgr_post, username, sessiontype, marker,
                users_data):
    """
    Returns a DataFrame line with result of romberg marker.
    """
    task_pre, task_oczy_pre, task_bacznosc_pre, task_gabka_pre, \
        task_poznawcze_pre = analysis_user_file.get_data(wbb_mgr_pre)
    task_post, task_oczy_post, task_bacznosc_post, task_gabka_post, \
        task_poznawcze_post = analysis_user_file.get_data(wbb_mgr_post)
    results = pd.DataFrame()

    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        results[name] = pd.Series([t])

    x, y = analysis_helper.remove_baseline(task_pre)
    stanie_pre = get_marker(marker, task_pre, x, y)
    for name, t in zip(['oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):
        x, y = analysis_helper.remove_baseline(t)
        if analysis_user_file.user_task_checker(username, name, users_data):
            results['{}_{}'.format(name, 'pre')] \
                = pd.Series(romberg(get_marker(marker, t, x, y), stanie_pre))
        else:
            results['{}_{}'.format(name, 'pre')] = pd.Series([' '])

    x, y = analysis_helper.remove_baseline(task_post)
    stanie_post = get_marker(marker, task_post, x, y)
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):
        x, y = analysis_helper.remove_baseline(t)
        if analysis_user_file.user_task_checker(username, name, users_data):
            results['{}_{}'.format(name, 'post')] \
                = pd.Series(romberg(get_marker(marker, t, x, y), stanie_post))
        else:
            results['{}_{}'.format(name, 'post')] = pd.Series([' '])

    return results

def get_dual_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype, marker,
                     users_data):
    # user_data_velocity = pd.DataFrame()
    user_data_x = pd.DataFrame()
    user_data_y = pd.DataFrame()
    user_data = pd.DataFrame()
    task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre, \
           task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre, \
           task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre = analysis_user_file.get_dual_data_fragments(wbb_mgr_pre)
    task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post, \
           task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post, \
           task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post = analysis_user_file.get_dual_data_fragments(wbb_mgr_post)
    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        # user_data_velocity[name] = pd.Series([t])
        user_data_x[name] = pd.Series([t])
        user_data_y[name] = pd.Series([t])
        user_data[name] = pd.Series([t])

    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre,
                        task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre,
                        task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre]):

        x, y = analysis_helper.remove_baseline(t)

        task = ""
        for char in name:
            if char == '_':
                break
            else:
                task += char

        if analysis_user_file.user_task_checker(username, task, users_data):
            user_data_x['{}_{}'.format(name, 'pre')] \
                = pd.Series(get_marker(marker, t, x, y, axis='x'))
            user_data_y['{}_{}'.format(name, 'pre')] \
                = pd.Series(get_marker(marker, t, x, y, axis='y'))
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series(get_marker(marker, t, x, y))
        else:
            user_data_x['{}_{}'.format(name, 'pre')] = pd.Series([' '])
            user_data_y['{}_{}'.format(name, 'pre')] = pd.Series([' '])
            user_data['{}_{}'.format(name, 'pre')] = pd.Series([' '])

    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post,
                        task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post,
                        task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post]):

        x, y = analysis_helper.remove_baseline(t)

        task = ""
        for char in name:
            if char == '_':
                break
            else:
                task += char

        if analysis_user_file.user_task_checker(username, task, users_data):
            user_data_x['{}_{}'.format(name, 'post')] \
                = pd.Series(get_marker(marker, t, x, y, axis='x'))
            user_data_y['{}_{}'.format(name, 'post')] \
                = pd.Series(get_marker(marker, t, x, y, axis='y'))
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series(get_marker(marker, t, x, y))
        else:
            user_data_x['{}_{}'.format(name, 'post')] = pd.Series([' '])
            user_data_y['{}_{}'.format(name, 'post')] = pd.Series([' '])
            user_data['{}_{}'.format(name, 'post')] = pd.Series([' '])

    return user_data, user_data_x, user_data_y