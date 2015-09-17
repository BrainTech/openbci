from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.collections import LineCollection
from random import randint


def get_file_list(param):
    file_list = []
    for paths, subcatalogs, files in walk(r'./'+param+'_data'):
        for file in files:
            if 'resampled' in file and 'psy' not in file and 'adjust' not in file:
                file = cut_extension(file)
                file_list.append(path.join(paths, file))
    file_set = set(file_list)
    file_list = list(file_set)
    return file_list

def cut_extension(file):
    string = file[0]
    for char in range(1, len(file)):
        if file[char] == '.':
            return string
        else:
            string += file[char]

def get_info_from_filename(filename):
    username = ' '
    prefix = ''
    i = 0
    for iter in range(0, len(filename)):
        if filename[iter] == '/':
            i += 1
        if i == 3:
            prefix +=filename[iter]
        if i == 4:
            username = filename[iter+1:iter+5]
            break
    prefix = prefix[1:]
    return username, prefix

def get_read_manager(file_name):
    w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       file_name+'.obci.tag')

    w = wii_filter_signal(w, 33.5/2, 2, use_filtfilt=True)

    return w

def get_read_manager_dual(file_name):
    tag_name = ''
    i = 0
    for char in file_name:
        tag_name += char
        if char == '/':
            i += 1
        if i == 4:
            break

    w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       tag_name +'adjusted_tag.tag')
    return w

def get_data_fragments(wbb_mgr):
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

def get_data_fragment(wbb_mgr, start_tag, end_tag):

    data = wii_cut_fragments(wbb_mgr, start_tag_name=start_tag,
                             end_tags_names=[end_tag], TS=True)
    x, y = remove_baseline(data)
    return x, y

def get_dual_data_fragments(wbb_mgr):
    task_stanie_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_zgodny1_start',
                                    end_tags_names=['ss_zgodny1_stop'], TS=True)
    task_stanie_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_zgodny2_start',
                                    end_tags_names=['ss_zgodny2_stop'], TS=True)
    task_stanie_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_niezgodny1_start',
                                    end_tags_names=['ss_niezgodny1_stop'], TS=True)
    task_stanie_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_niezgodny2_start',
                                    end_tags_names=['ss_niezgodny2_stop'], TS=True)

    task_bacznosc_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_zgodny1_start',
                                    end_tags_names=['ss_bacznosc_zgodny1_stop'], TS=True)
    task_bacznosc_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_zgodny2_start',
                                    end_tags_names=['ss_bacznosc_zgodny2_stop'], TS=True)
    task_bacznosc_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_niezgodny1_start',
                                    end_tags_names=['ss_bacznosc_niezgodny1_stop'], TS=True)
    task_bacznosc_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_niezgodny2_start',
                                    end_tags_names=['ss_bacznosc_niezgodny2_stop'], TS=True)

    task_gabka_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_zgodny1_start',
                                    end_tags_names=['ss_gabka_zgodny1_stop'], TS=True)
    task_gabka_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_zgodny2_start',
                                    end_tags_names=['ss_gabka_zgodny2_stop'], TS=True)
    task_gabka_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_niezgodny1_start',
                                    end_tags_names=['ss_gabka_niezgodny1_stop'], TS=True)
    task_gabka_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_niezgodny2_start',
                                    end_tags_names=['ss_gabka_niezgodny2_stop'], TS=True)

    return task_stanie_zgodny1, task_stanie_zgodny2, task_stanie_niezgodny1, task_stanie_niezgodny2, \
           task_bacznosc_zgodny1, task_bacznosc_zgodny2, task_bacznosc_niezgodny1, task_bacznosc_niezgodny2, \
           task_gabka_zgodny1, task_gabka_zgodny2, task_gabka_niezgodny1, task_gabka_niezgodny2

def user_task_checker(user, task):
    if int(users_data[users_data['ID'] == user][task].values[0]):
        return True
    else:
        return False

def get_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype, alt_username):
    user_data_velocity = pd.DataFrame()
    user_data_mean_dist_x = pd.DataFrame()
    user_data_mean_dist_y = pd.DataFrame()
    user_data_mean_dist = pd.DataFrame()
    task_pre, task_oczy_pre, task_bacznosc_pre, task_gabka_pre, \
        task_poznawcze_pre = get_data_fragments(wbb_mgr_pre)
    task_post, task_oczy_post, task_bacznosc_post, task_gabka_post, \
        task_poznawcze_post = get_data_fragments(wbb_mgr_post)

    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        user_data_velocity[name] = pd.Series([t])
        user_data_mean_dist_x[name] = pd.Series([t])
        user_data_mean_dist_y[name] = pd.Series([t])
        user_data_mean_dist[name] = pd.Series([t])
    base_velo = mean_velocity(np.vstack(remove_baseline(task_pre)), 33.5)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_pre, task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):

        x, y = remove_baseline(t)

        print_plots(x, y, name, alt_username, 'pre')

        if user_task_checker(username, name):
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([(mean_velocity(np.vstack((x,y)), 33.5)[0])/base_velo])
            user_data_mean_dist_x['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(x)])
            user_data_mean_dist_y['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(y)])
            user_data_mean_dist['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(x, y)])
        else:
            user_data_velocity['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_mean_dist_x['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_mean_dist_y['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_mean_dist['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])

    base_velo = mean_velocity(np.vstack(remove_baseline(task_post)), 33.5)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):

        x, y = remove_baseline(t)

        print_plots(x, y, name, alt_username, 'post')

        if user_task_checker(username, name):
            user_data_velocity['{}_{}'.format(name, 'post')] \
                = pd.Series([(mean_velocity(np.vstack((x,y)), 33.5)[0])/base_velo])
            user_data_mean_dist_x['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(x)])
            user_data_mean_dist_y['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(y)])
            user_data_mean_dist['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(x, y)])
        else:
            user_data_velocity['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_mean_dist_x['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_mean_dist_y['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_mean_dist['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
    return user_data_velocity, user_data_mean_dist_x, user_data_mean_dist_y, user_data_mean_dist

def remove_baseline(t):
    # fs = 33.5
    # x_baseline = t[0][1*fs:3*fs]
    # y_baseline = t[1][1*fs:3*fs]
    # x_baseline = sum(x_baseline)/len(x_baseline)
    # y_baseline = sum(y_baseline)/len(y_baseline)
    x = t[0]*22.5
    # x = (x - x_baseline)*22.5
    y = t[1]*13
    # y = (y - y_baseline)*13
    return x, y

def get_dual_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype):
    # user_data_velocity = pd.DataFrame()
    user_data_mean_dist_x = pd.DataFrame()
    user_data_mean_dist_y = pd.DataFrame()
    user_data_mean_dist = pd.DataFrame()
    task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre, \
           task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre, \
           task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre = get_dual_data_fragments(wbb_mgr_pre)
    task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post, \
           task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post, \
           task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post = get_dual_data_fragments(wbb_mgr_post)
    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        # user_data_velocity[name] = pd.Series([t])
        user_data_mean_dist_x[name] = pd.Series([t])
        user_data_mean_dist_y[name] = pd.Series([t])
        user_data_mean_dist[name] = pd.Series([t])

    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre,
                        task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre,
                        task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre]):

        x, y = remove_baseline(t)

        if username == 'WK88' and ('gabka' in name):
            user_data_mean_dist_x['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_mean_dist_y['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
            user_data_mean_dist['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            user_data_mean_dist_x['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(x)])
            user_data_mean_dist_y['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(y)])
            user_data_mean_dist['{}_{}'.format(name, 'pre')] \
                = pd.Series([get_mean_dist(x, y)])


    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post,
                        task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post,
                        task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post]):

        x, y = remove_baseline(t)

        if username == 'WK88' and ('gabka' in name):
            user_data_mean_dist_x['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_mean_dist_y['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data_mean_dist['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])

        else:
            user_data_mean_dist_x['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(x)])
            user_data_mean_dist_y['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(y)])
            user_data_mean_dist['{}_{}'.format(name, 'post')] \
                = pd.Series([get_mean_dist(x, y)])
    return user_data_mean_dist, user_data_mean_dist_x, user_data_mean_dist_y


def get_mean_dist(x, y=None):
    if y is None:
        return abs(np.mean(x - np.mean(x)))
    else:
        x -= np.mean(x)
        y -= np.mean(y)
        return np.mean(np.sqrt((x*x)+(y*y)))

def average(data):

    cols = ['stanie_zgodny', 'stanie_niezgodny',
            'bacznosc_zgodny', 'bacznosc_niezgodny',
            'gabka_zgodny', 'gabka_niezgodny']

    average_data = pd.DataFrame()
    average_data['username'] = pd.Series(data['username'])
    average_data['session_type'] = pd.Series(data['session_type'])
    for col in cols:
        average_col_pre = []
        average_col_post = []
        for row1, row2 in zip(data[col+'1_pre'].values, data[col+'2_pre'].values):
            if row1 == ' ' or row2 == ' ':
                average_col_pre.append(' ')
            else:
                average_col_pre.append((float(row1)+float(row2))/2)

        for row1, row2 in zip(data[col+'1_post'].values, data[col+'2_post'].values):
            if row1 == ' ' or row2 == ' ':
                average_col_pre[len(average_col_post)] = ' '
                average_col_post.append(' ')
            else:
                average_col_post.append((float(row1)+float(row2))/2)
        average_data['{}_{}'.format(col, 'pre')] \
            = pd.Series(average_col_pre, index=average_data.index)
        average_data['{}_{}'.format(col, 'post')] \
            = pd.Series(average_col_post, index=average_data.index)
    return average_data

def print_plots(x, y, task, user, param):
    x -= np.mean(x)
    y -= np.mean(y)
    r = np.sqrt(x*x + y*y)

    # fft = np.fft.fft(x)

    code = str(len(task)-2) + str(param) + str(unichr(randint(65, 90))) + user[5]

    t = np.linspace(0, 20, len(x))

    ax_xy = plt.subplot2grid((2, 2), (0, 1), rowspan=2)
    ax_xy.set_title(code)
    t_col = np.linspace(0, 10, 780)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(-3, 3, 0.2))
    plt.yticks(np.arange(-3, 3, 0.2))
    plt.tick_params(axis='both', labelsize=7)

    ax_x = plt.subplot2grid((2, 2), (0, 0))
    ax_x.set_ylabel('X')
    if task == 'ss':
        ax_x.set_title('stanie')
    else:
        ax_x.set_title(task[3:])
    points = np.array([t, x]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(0, 20)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(0, 20, 1))
    plt.yticks(np.arange(-3, 3, 0.5))
    plt.tick_params(axis='both', labelsize=7)

    ax_y = plt.subplot2grid((2, 2), (1, 0))
    ax_y.set_ylabel('Y')
    points = np.array([t, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(0, 20)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(0, 20, 1))
    plt.yticks(np.arange(-3, 3, 0.5))
    plt.tick_params(axis='both', labelsize=7)

    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()

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
                self.wbb_pre = get_read_manager(file)
            if self.username in file and 'post' in file[10:]:
                # print(file)
                self.wbb_post = get_read_manager(file)

        # for file in file_list_dual:
        #     if self.username in file and 'pre' in file:
        #         self.wbb_dual_pre = get_read_manager_dual(file)
        #     if self.username in file and 'post' in file:
        #         self.wbb_dual_post = get_read_manager_dual(file)
        # if user_task_checker(self.username, 'pre_post'):
        #     self.velo, self.mean_dist_x, self.mean_dist_y, self.mean_dist = \
        #         get_markers(self.wbb_pre, self.wbb_post, self.username, self.session_type, self.alt_username)
        # else:
        #     self.velo = None
        #     self.mean_dist = None
        #     self.mean_dist_x = None
        #     self.mean_dist_y = None
        # if user_task_checker(self.username, 'dual'):
        #     self.dual_dist, self.dual_dist_x, self.dual_dist_y = \
        #         get_dual_markers(self.wbb_dual_pre, self.wbb_dual_post, self.username, self.session_type)
        # else:
        #     self.dual_dist = None
        #     self.dual_dist_x = None
        #     self.dual_dist_y = None
        # self.dual_dist = average(self.dual_dist)
        # self.dual_dist_x = average(self.dual_dist_x)
        # self.dual_dist_y = average(self.dual_dist_y)

if __name__ == '__main__':
    users_data = pd.read_csv('./users.csv', index_col=0, dtype='str')
    users_names = users_data['ID'].values

    file_list = get_file_list('pre_post')
    file_list_dual = get_file_list('dual')

    users = []
    for user in users_names:
        user_object = User(user)
        users.append(user_object)

    users = set(users)
    users = list(users)

    # markers_velo = pd.DataFrame()
    # markers_mean_x = pd.DataFrame()
    # markers_mean_y = pd.DataFrame()
    # markers_mean = pd.DataFrame()
    # markers_dual_mean_x = pd.DataFrame()
    # markers_dual_mean_y = pd.DataFrame()
    # markers_dual_mean = pd.DataFrame()

    # for user in users:
    #     markers_velo = markers_velo.append(user.velo)
    #     markers_mean_x = markers_mean_x.append(user.mean_dist_x)
    #     markers_mean_y = markers_mean_y.append(user.mean_dist_y)
    #     markers_mean = markers_mean.append(user.mean_dist)
    #     markers_dual_mean_x = markers_dual_mean_x.append(user.dual_dist_x)
    #     markers_dual_mean_y = markers_dual_mean_y.append(user.dual_dist_y)
    #     markers_dual_mean = markers_dual_mean.append(user.dual_dist)
    #
    # markers_dual_mean = average(markers_dual_mean)
    # markers_dual_mean_x = average(markers_dual_mean_x)
    # markers_dual_mean_y = average(markers_dual_mean_y)
    #
    # markers_velo.to_csv("data/markers_velo.csv", sep=',')
    # markers_mean_x.to_csv("data/markers_mean_x.csv", sep=',')
    # markers_mean_y.to_csv("data/markers_mean_y.csv", sep=',')
    # markers_mean.to_csv("data/markers_mean.csv", sep=',')
    # markers_dual_mean_x.to_csv("data/markers_dual_mean_x.csv", sep=',')
    # markers_dual_mean_y.to_csv("data/markers_dual_mean_y.csv", sep=',')
    # markers_dual_mean.to_csv("data/markers_dual_mean.csv", sep=',')

    tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']
    fib = [1, 2, 3, 5, 8]

    for task in tasks:
        for user in users:
            if user.wbb_pre is not None and user.wbb_post is not None:
                param = randint(0, 9)
                if param in fib:
                    x, y = get_data_fragment(user.wbb_post, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, param)
                    x, y = get_data_fragment(user.wbb_pre, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, '0')
                else:
                    x, y = get_data_fragment(user.wbb_pre, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, param)
                    x, y = get_data_fragment(user.wbb_post, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, '3')


