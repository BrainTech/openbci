#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from os import *
import analysis_user_file
import analysis_helper
import pandas as pd

if __name__ == '__main__':
    # create a list of all files in subfolders of this location
    file_list = []
    for paths, subcatalogs, files in walk(r'./pre_post_data'):
        for file in files:
            if file not in file_list and 'resampled' in file:
                file_list.append(file)
    USERS = analysis_helper.get_users(file_list)

    # get users' tasks' data info (if it's good enough for analysis)
    users_data = pd.read_csv('~/data/users_tasks.csv', index_col=0,
                             dtype='str')

    # count markers
    complete = 0
    markers_path = pd.DataFrame()
    markers_ellipse = pd.DataFrame()
    markers_velocity = pd.DataFrame()
    markers_romberg = pd.DataFrame()
    for user in USERS:
        user = analysis_user_file.User(user, users_tasks)
        if user.pre_post_file and user.pre_post_file.obci_markers:
            markers_path = markers_path.append(user.pre_post_file.obci_markers[0])
            markers_ellipse = markers_ellipse.append(user.pre_post_file.obci_markers[1])
            markers_velocity = markers_velocity.append(user.pre_post_file.obci_markers[2])
            markers_romberg = markers_romberg.append(user.pre_post_file.romberg)
        if user.complete:
            complete += 1
    print("Complete cases:", complete)

    # save data to csv files
    markers_path.to_csv("data/markers_path.csv", sep=',')
    markers_ellipse.to_csv("data/markers_ellipse.csv", sep=',')
    markers_velocity.to_csv("data/markers_velocity.csv", sep=',')
    markers_romberg.to_csv("data/markers_romberg.csv", sep=',')

