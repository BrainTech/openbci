#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
# About script:
#       This is the first script created during the analysis of Ventures data.
#   It counts first markers (COP, elipse, velocity, romberg) and try to 
#   arrange data somehow.

from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.wii_preprocessing import *
import analysis_helper

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd


def get_data(wbb_mgr):
    """
    Returns specific fragments of signal.
    """
    task_stanie = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_start',
                                    end_tags_names=['ss_stop'], TS=True)
    task_oczy = wii_cut_fragments(wbb_mgr,
                                  start_tag_name='ss_oczy_start',
                                  end_tags_names=['ss_oczy_stop'], TS=True)
    task_bacznosc = wii_cut_fragments(wbb_mgr,
                                      start_tag_name='ss_bacznosc_start',
                                      end_tags_names=['ss_bacznosc_stop'], TS=True)
    task_gabka = wii_cut_fragments(wbb_mgr,
                                   start_tag_name='ss_gabka_start',
                                   end_tags_names=['ss_gabka_stop'], TS=True)
    task_poznawcze = wii_cut_fragments(wbb_mgr,
                                       start_tag_name='ss_poznawcze_start',
                                       end_tags_names=['ss_poznawcze_stop'], TS=True)
    return task_stanie, task_oczy, task_bacznosc, task_gabka, task_poznawcze

def get_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype):
    """
    Returns the following markers:
    - COP
    - ellipse 95% area
    - velocity
    """
    user_data_elipse = pd.DataFrame()
    user_data = pd.DataFrame()
    user_data_velocity = pd.DataFrame()
    task_pre, task_oczy_pre, task_bacznosc_pre, task_gabka_pre, \
        task_poznawcze_pre = get_data(wbb_mgr_pre)
    task_post, task_oczy_post, task_bacznosc_post, task_gabka_post, \
        task_poznawcze_post = get_data(wbb_mgr_post)
    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        user_data[name] = pd.Series([t])
        user_data_elipse[name] = pd.Series([t])
        user_data_velocity[name] = pd.Series([t])
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_pre, task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):

        x, y = remove_baseline(t, username, name)
        if len(x) < 490:
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_elipse['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0]])
            user_data_elipse['{}_{}'.format(name, 'pre')] \
                = pd.Series([wii_confidence_ellipse_area(x, y, f_value=2.3)])
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([wii_mean_velocity(wbb_mgr_pre, x, y)][0])

    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):

        x, y = remove_baseline(t, username, name)

        if len(x) < 490 or user_data[user_data['username']==username][name+'_pre'].values[0] == ' ':
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_elipse['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_velocity['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_elipse['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])

        else:
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series([wii_COP_path(wbb_mgr_post, x, y, plot=False)[0]])
            user_data_elipse['{}_{}'.format(name, 'post')] \
                = pd.Series([wii_confidence_ellipse_area(x, y, f_value=2.3)])
            user_data_velocity['{}_{}'.format(name, 'post')] \
                = pd.Series([wii_mean_velocity(wbb_mgr_post, x, y)][0])

    return user_data, user_data_elipse, user_data_velocity

def remove_baseline(t, user, task):
    """
    Returns x and y data, counts its baseline and cuts it off.
    """
    fs = len(t[0])/20
    x_baseline = t[0][1*fs:3*fs]
    y_baseline = t[1][1*fs:3*fs]
    x_baseline = sum(x_baseline)/len(x_baseline)
    y_baseline = sum(y_baseline)/len(y_baseline)
    x = t[0][0*fs:20*fs]
    x = (x - x_baseline)*22.5
    y = t[1][0*fs:20*fs]
    y = (y - y_baseline)*13

    # plt.plot(x, y)
    # plt.title('{} {} {} {}'.format(user, task, len(x) - len(list(set(x))), len(y) - len(list(set(y)))))
    # plt.xlim(-5, 5)
    # plt.ylim(-5, 5)
    # plt.show()
    return x, y

def get_romberg(wbb_mgr_pre, wbb_mgr_post, username, sessiontype):
    """
    Returns a DataFrame line with result of romberg marker (for COP).
    """
    task_pre, task_oczy_pre, task_bacznosc_pre, task_gabka_pre, \
        task_poznawcze_pre = get_data(wbb_mgr_pre)
    task_post, task_oczy_post, task_bacznosc_post, task_gabka_post, \
        task_poznawcze_post = get_data(wbb_mgr_post)
    results = pd.DataFrame()

    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        results[name] = pd.Series([t])

    x, y = remove_baseline(task_pre, username, name)
    stanie_pre_path = wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_pre, task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):
        x, y = remove_baseline(t, username, name)
        if len(x) < 490:
            results['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            results['{}_{}'.format(name, 'pre')] \
                = pd.Series(stanie_pre_path/wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0])
    x, y = remove_baseline(task_post, username, name)
    stanie_post_path = wii_COP_path(wbb_mgr_post, x, y, plot=False)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):
        x, y = remove_baseline(t, username, name)
        if len(x) < 490 or results[results['username']==username][name+'_pre'].values[0] == ' ':
            results['{}_{}'.format(name, 'post')] = pd.Series([' '])
            results['{}_{}'.format(name, 'pre')] = pd.Series([' '])
        else:
            results['{}_{}'.format(name, 'post')] \
                = pd.Series(stanie_post_path/[wii_COP_path(wbb_mgr_post, x, y, plot=False)][0])

    return results

def save_data():
    """
    Main function of this script, creates the instances of User, counts
    markers and save data into csv files.
    """
    complete = 0
    markers_path = pd.DataFrame()
    markers_ellipse = pd.DataFrame()
    markers_velocity = pd.DataFrame()
    markers_romberg = pd.DataFrame()
    for user in USERS:
        user = User(user)
        if user.pre_post_file and user.pre_post_file.obci_markers:
            markers_path = markers_path.append(user.pre_post_file.obci_markers[0])
            markers_ellipse = markers_ellipse.append(user.pre_post_file.obci_markers[1])
            markers_velocity = markers_velocity.append(user.pre_post_file.obci_markers[2])
            markers_romberg = markers_romberg.append(user.pre_post_file.romberg)
        if user.complete:
            complete += 1
    print("Complete cases:", complete)

    markers_path.to_csv("data/markers_path.csv", sep=',')
    markers_ellipse.to_csv("data/markers_ellipse.csv", sep=',')
    markers_velocity.to_csv("data/markers_velocity.csv", sep=',')
    markers_romberg.to_csv("data/markers_romberg.csv", sep=',')

if __name__ == '__main__':

    # create a list of all files in subfolders of this location
    file_list = []
    for paths, subcatalogs, files in walk(r'./pre_post_data'):
        for file in files:
            if file not in file_list and 'resampled' in file:
                file_list.append(file)

    # changes file names to tokens
    USERS = get_users(file_list)

    save_data()

