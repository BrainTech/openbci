from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import numpy as np
from matplotlib import pyplot as plt
from scipy import signal
import scipy
import pandas as pd

import markers, next_markers

def filter_signal(x):
    b, a = signal.butter(2, 0.5/(33.5/2), 'high')
    return signal.filtfilt(b, a, x)

def get_data_fragment(wbb_mgr, tag):
    data = wii_cut_fragments(wbb_mgr, start_tag_name=tag+'_start',
                             end_tags_names=[tag+'_stop'], TS=True)
    x = data[0]*22.5
    y = data[1]*13
    return x, y

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
                self.wbb_pre = next_markers.get_read_manager(file)
            if self.username in file and 'post' in file[10:]:
                # print(file)
                self.wbb_post = next_markers.get_read_manager(file)

def user_task_checker(user, task):
    if int(users_data[users_data['ID'] == user][task].values[0]):
        return True
    else:
        return False

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

    file_list = next_markers.get_file_list('pre_post')

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

                    x, y = get_data_fragment(user.wbb_pre, task)
                    pre_data = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    post_data = markers.marker(marker, user.wbb_post, x, y)
                    # plt.plot(y, x)

                    x, y = get_data_fragment(user.wbb_pre, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    pre_data_f = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    post_data_f = markers.marker(marker, user.wbb_post, x, y)
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
                        if user_task_checker(user.username, task):
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
                x, y = get_data_fragment(user.wbb_pre, 'ss')
                pre_data_base = markers.marker(marker, user.wbb_pre, x, y)
                x, y = get_data_fragment(user.wbb_post, 'ss')
                post_data_base = markers.marker(marker, user.wbb_post, x, y)

                x, y = get_data_fragment(user.wbb_pre, 'ss')
                x = filter_signal(x)
                y = filter_signal(y)
                pre_data_f_base = markers.marker(marker, user.wbb_pre, x, y)
                x, y = get_data_fragment(user.wbb_post, 'ss')
                x = filter_signal(x)
                y = filter_signal(y)
                post_data_f_base = markers.marker(marker, user.wbb_post, x, y)

            for task in tasks:
                if user.wbb_pre is not None and user.wbb_post is not None:

                    x, y = get_data_fragment(user.wbb_pre, task)
                    pre_data = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    post_data = markers.marker(marker, user.wbb_post, x, y)

                    x, y = get_data_fragment(user.wbb_pre, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    pre_data_f = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    post_data_f = markers.marker(marker, user.wbb_post, x, y)

                    for name, t in zip(['nonfilt_xy_pre', 'nonfilt_xy_post', 'nonfilt_x_pre', 'nonfilt_x_post', 'nonfilt_y_pre', 'nonfilt_y_post',
                                        'filt_xy_pre', 'filt_xy_post', 'filt_x_pre', 'filt_x_post', 'filt_y_pre', 'filt_y_post'],
                                       [pre_data_base[0]/pre_data[0], post_data_base[0]/post_data[0], pre_data_base[1]/pre_data[1], post_data_base[1]/post_data[1], pre_data_base[2]/pre_data[2], post_data_base[2]/post_data[2],
                                        pre_data_f_base[0]/pre_data_f[0], post_data_f_base[0]/post_data_f[0], pre_data_f_base[1]/pre_data_f[1], post_data_f_base[1]/post_data_f[1], pre_data_f_base[2]/pre_data_f[2], post_data_f_base[2]/post_data_f[2]]):
                        if (marker == 'COP' or marker == 'elipsa') and 'xy' not in name:
                            continue
                        if user_task_checker(user.username, task):
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

                    x, y = get_data_fragment(user.wbb_pre, task)
                    pre_data = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    post_data = markers.marker(marker, user.wbb_post, x, y)

                    x, y = get_data_fragment(user.wbb_pre, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    pre_data_f = markers.marker(marker, user.wbb_pre, x, y)
                    x, y = get_data_fragment(user.wbb_post, task)
                    x = filter_signal(x)
                    y = filter_signal(y)
                    post_data_f = markers.marker(marker, user.wbb_post, x, y)

                    for name, t in zip(['nonfilt_xy', 'nonfilt_x', 'nonfilt_y',
                                        'filt_xy', 'filt_x', 'filt_y'],
                                       [markers.poly(pre_data[0], post_data[0]), markers.poly(pre_data[1], post_data[1]), markers.poly(pre_data[2], post_data[2]),
                                        markers.poly(pre_data_f[0], post_data_f[0]), markers.poly(pre_data_f[1], post_data_f[1]), markers.poly(pre_data_f[2], post_data_f[2])]):
                        if (marker == 'COP' or marker == 'elipsa') and 'xy' not in name:
                            continue
                        if user_task_checker(user.username, task):
                            huge_line['{}_{}_{}_{}'.format('poly', marker, task, name)] = pd.Series([t])
                        else:
                            huge_line['{}_{}_{}_{}'.format('poly', marker, task, name)] = pd.Series([' '])


        poly = poly.append(huge_line, ignore_index=True)

    huge_data = pd.concat([huge_data, poly], axis=1, join_axes=[huge_data.index])

    huge_data.to_csv("data/i_love_huge_data.csv", sep=',')

    print(huge_data)







