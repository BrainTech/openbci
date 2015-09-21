#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *
import pandas as pd
import analysis_markers, analysis_helper, analysis_user_file

class User(object):
    def __init__(self, user):
        self.username = user
        # print(user)
        self.session_type = users_data[users_data['ID']==self.username]['session_type'].values[0]
        self.alt_username = users_data[users_data['ID']==self.username]['alt_ID'].values[0]
        self.wbb_post = None
        self.wbb_pre = None
        for file in file_list:
            if self.username in file and 'pre' in file[10:]:
                # print(file)
                self.wbb_pre = analysis_helper.get_read_manager(file)
            if self.username in file and 'post' in file[10:]:
                # print(file)
                self.wbb_post = analysis_helper.get_read_manager(file)

if __name__ == '__main__':
    users_data = pd.read_csv('./users.csv', index_col=0, dtype='str')
    users_names = users_data['ID'].values

    tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']
    marks = ['COP', 'elipsa', 'predkosc', 'odleglosc']
    mods = ['axis', 'romberg', 'poly']
    types = ['pre', 'post']
    filt = ['filtered', 'nonfilt']
    ax = ['xy', 'x', 'y']
    # MOD_MARKER_TASK_FILT_AXIS_TYPE

    file_list = analysis_helper.get_file_list('pre_post')

    users = []
    for user in users_names:
        user_object = User(user)
        users.append(user_object)

    huge_data = pd.DataFrame()
    i = 0
        ######## AXIS ########

    for user in users:
        huge_line = pd.DataFrame()
        for name, t in zip(['username', 'session_type'], [user.username, user.session_type]):
            huge_line[name] = pd.Series([t])
        for marker in marks:
            for task in tasks:
                if user.wbb_pre is not None and user.wbb_post is not None:

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    pre_data = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    post_data = analysis_markers.get_marker(marker, user.wbb_post, x, y)
                    # plt.plot(y, x)

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    pre_data_f = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    post_data_f = analysis_markers.get_marker(marker, user.wbb_post, x, y)
                    # plt.plot(y, x, color='r')
                    # plt.tight_layout()
                    # mng = plt.get_current_fig_manager()
                    # mng.resize(*mng.window.maxsize())
                    # plt.show()

                    for name, t in zip(['nonfilt_xy_pre', 'nonfilt_xy_post', 'nonfilt_x_pre', 'nonfilt_x_post', 'nonfilt_y_pre', 'nonfilt_y_post',
                                        'filt_xy_pre', 'filt_xy_post', 'filt_x_pre', 'filt_x_post', 'filt_y_pre', 'filt_y_post'],
                                       [pre_data[0], post_data[0], pre_data[1], post_data[1], pre_data[2], post_data[2],
                                        pre_data_f[0], post_data_f[0], pre_data_f[1], post_data_f[1], pre_data_f[2], post_data_f[2]]):
                        if (marker == 'COP' or marker == 'elipsa') and 'xy' not in name:
                            continue
                        if analysis_user_file.user_task_checker(user.username, task):
                            huge_line['{}_{}_{}_{}'.format('axis', marker, task, name)] = pd.Series([t])
                        else:
                            huge_line['{}_{}_{}_{}'.format('axis', marker, task, name)] = pd.Series([' '])

        huge_data = huge_data.append(huge_line, ignore_index=True)

        ######## ROMBERG ########
    romberg = pd.DataFrame()

    tasks = ['ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']

    for user in users:
        huge_line = pd.DataFrame()
        for marker in marks:

            if user.wbb_pre is not None and user.wbb_post is not None:
                x, y = analysis_user_file.get_data_fragment(user.wbb_pre, 'ss')
                pre_data_base = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                x, y = analysis_user_file.get_data_fragment(user.wbb_post, 'ss')
                post_data_base = analysis_markers.get_marker(marker, user.wbb_post, x, y)

                x, y = analysis_user_file.get_data_fragment(user.wbb_pre, 'ss')
                x = analysis_markers.filter_signal(x)
                y = analysis_markers.filter_signal(y)
                pre_data_f_base = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                x, y = analysis_user_file.get_data_fragment(user.wbb_post, 'ss')
                x = analysis_markers.filter_signal(x)
                y = analysis_markers.filter_signal(y)
                post_data_f_base = analysis_markers.get_marker(marker, user.wbb_post, x, y)

            for task in tasks:
                if user.wbb_pre is not None and user.wbb_post is not None:

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    pre_data = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    post_data = analysis_markers.get_marker(marker, user.wbb_post, x, y)

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    pre_data_f = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    post_data_f = analysis_markers.get_marker(marker, user.wbb_post, x, y)

                    for name, t in zip(['nonfilt_xy_pre', 'nonfilt_xy_post', 'nonfilt_x_pre', 'nonfilt_x_post', 'nonfilt_y_pre', 'nonfilt_y_post',
                                        'filt_xy_pre', 'filt_xy_post', 'filt_x_pre', 'filt_x_post', 'filt_y_pre', 'filt_y_post'],
                                       [pre_data_base[0]/pre_data[0], post_data_base[0]/post_data[0], pre_data_base[1]/pre_data[1], post_data_base[1]/post_data[1], pre_data_base[2]/pre_data[2], post_data_base[2]/post_data[2],
                                        pre_data_f_base[0]/pre_data_f[0], post_data_f_base[0]/post_data_f[0], pre_data_f_base[1]/pre_data_f[1], post_data_f_base[1]/post_data_f[1], pre_data_f_base[2]/pre_data_f[2], post_data_f_base[2]/post_data_f[2]]):
                        if (marker == 'COP' or marker == 'elipsa') and 'xy' not in name:
                            continue
                        if analysis_user_file.user_task_checker(user.username, task):
                            huge_line['{}_{}_{}_{}'.format('romberg', marker, task, name)] = pd.Series([t])
                        else:
                            huge_line['{}_{}_{}_{}'.format('romberg', marker, task, name)] = pd.Series([' '])

        romberg = romberg.append(huge_line, ignore_index=True)

    huge_data = pd.concat([huge_data, romberg], axis=1, join_axes=[huge_data.index])

    ######## POLY ########
    poly = pd.DataFrame()
    tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']

    for user in users:
        huge_line = pd.DataFrame()

        for marker in marks:
            for task in tasks:
                if user.wbb_pre is not None and user.wbb_post is not None:

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    pre_data = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    post_data = analysis_markers.get_marker(marker, user.wbb_post, x, y)

                    x, y = analysis_user_file.get_data_fragment(user.wbb_pre, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    pre_data_f = analysis_markers.get_marker(marker, user.wbb_pre, x, y)
                    x, y = analysis_user_file.get_data_fragment(user.wbb_post, task)
                    x = analysis_markers.filter_signal(x)
                    y = analysis_markers.filter_signal(y)
                    post_data_f = analysis_markers.get_marker(marker, user.wbb_post, x, y)

                    for name, t in zip(['nonfilt_xy', 'nonfilt_x', 'nonfilt_y',
                                        'filt_xy', 'filt_x', 'filt_y'],
                                       [analysis_markers.poly(pre_data[0], post_data[0]), analysis_markers.poly(pre_data[1], post_data[1]), analysis_markers.poly(pre_data[2], post_data[2]),
                                        analysis_markers.poly(pre_data_f[0], post_data_f[0]), analysis_markers.poly(pre_data_f[1], post_data_f[1]), analysis_markers.poly(pre_data_f[2], post_data_f[2])]):
                        if (marker == 'COP' or marker == 'elipsa') and 'xy' not in name:
                            continue
                        if analysis_user_file.user_task_checker(user.username, task):
                            huge_line['{}_{}_{}_{}'.format('poly', marker, task, name)] = pd.Series([t])
                        else:
                            huge_line['{}_{}_{}_{}'.format('poly', marker, task, name)] = pd.Series([' '])


        poly = poly.append(huge_line, ignore_index=True)

    huge_data = pd.concat([huge_data, poly], axis=1, join_axes=[huge_data.index])

    huge_data.to_csv("data/pre_post_huge_data.csv", sep=',')

    print(huge_data)
