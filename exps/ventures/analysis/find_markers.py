#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
# About script:
#       It's the first script created during the analysis of Ventures data.
#   Its aim was to count first markers and try to arrange data somehow.

from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

def decode_token(path):
    """
    Extracts tokens form a file path.
    """
    str = ""
    elements_list = []
    for char in path:
        if char == '_':
            elements_list.append(str)
            str = ""
        else:
            str += char
    elements_list.append(str)
    return elements_list

def get_users(file_list):
    """
    Extracts user names form file paths.
    """
    users_list = []
    for elem in file_list:
        if (elem[0].upper() not in users_list) and (len(elem[0]) == 4) \
                and (elem[0][2].isdigit()):
            users_list.append(elem[0].upper())
    return users_list

def one_user_files(user, file_list):
    """
    Creates a list of files concerning one user.
    """
    one_user_list = []
    for elem in file_list:
        if elem[0] == user:
            one_user_list.append(elem)
    return one_user_list

def one_user_type_files(string, one_user_files):
    """
    Returns those strings from given list, which contains given string.
    """
    one_user_type_list = []
    for list in one_user_files:
        for elem in list:
            if elem == string:
                one_user_type_list.append(list)
    return one_user_type_list


def get_date_from_path(file):
    """
    For specific files, extracts date from file as a string.
    """
    file = str(file)
    for i in range(0, len(file)-3):
        if file[i:i+3] == "201":
            return file[i:i+19]

def to_int(date):
    """
    Changes given data from string to integer.
    """
    str = ""
    i = 0
    for i in range(0, 19):
        if date[i].isdigit():
            str += date[i]
        elif date[i:i+3] == "Jan":
            str += "01"
        elif date[i:i+3] == "Feb":
            str += "02"
        elif date[i:i+3] == "Mar":
            str += "03"
        elif date[i:i+3] == "Apr":
            str += "04"
        elif date[i:i+3] == "May":
            str += "05"
        elif date[i:i+3] == "Jun":
            str += "06"
        elif date[i:i+3] == "Jul":
            str += "07"
        elif date[i:i+3] == "Aug":
            str += "08"
        elif date[i:i+3] == "Sep":
            str += "09"
        elif date[i:i+3] == "Oct":
            str += "10"
        elif date[i:i+3] == "Nov":
            str += "11"
        elif date[i:i+3] == "Dec":
            str += "12"
    return int(str)

class User(object):
    """
    Object of this class contains much information about one user files.
    Especially, it extracts one path to needed files.
    After arranging data in neat folders, it is no longer as important.
    """

    def __init__(self, name):
        self.name = name.upper()
        print("*** ", self.name, " ***")
        self.complete = False
        self.session_type = self.get_session_type()
        self.all_files_list = self.get_files()
        self.all_files_list = self.remove_duplicate(self.all_files_list)
        self.pretest_files_list = self.one_type_files("pretest", "dual")
        self.postest_files_list = self.one_type_files("post", "dual")
        self.pretest = self.get_proper(self.pretest_files_list)
        self.postest = self.get_proper(self.postest_files_list)
        if self.pretest is not None and self.postest is not None:
            self.complete = True
        self.pretest = self.cut_extension(self.pretest)
        self.postest = self.cut_extension(self.postest)
        if self.pretest is not None and self.postest is not None:
            self.pre_post_file = File(self.find_file(self.pretest),
                                      self.find_file(self.postest), self)
        else:
            self.pre_post_file = None

    def get_session_type(self):
        """
        Checks in users.csv (in folder named 'data', provide a proper path!)
        which type of session this user was performing.
        """
        data = pd.read_csv('users.csv', index_col=0, dtype='str')
        if self.name in data['ID'].values:
            return data[data['ID']==self.name]['session_type'].values[0]
        else:
            return None

    def get_files(self):
        """
        Gets data files from a folder 'pre_post_data' (data was arranged there
        as: pre_post_data/username/pre_or_post/files_of_user
        """
        list = []
        for paths, subcatalogs, files in walk(r'./pre_post_data'):
            for file in files:
                if self._compare_name(file) and 'resampled' in file:
                    list.append(file)
        return list

    def _compare_name(self, file):
        """
        Checks if a file concerns the object.
        """
        name_str = str(self.name)
        file_str = str(file)
        if name_str in file_str:
            return True
        else:
            return False

    def remove_duplicate(self, mylist):
        """
        Removes duplicates from list
        """
        if not mylist:
            return None
        mylist = set(mylist)
        return list(mylist)

    def one_type_files(self, substring, notsubstring="tegonapewnoniema"):
        """
        Returns a list of strings containing those which have substring
        and don't have 'notsubstring'.
        """
        list = []
        for file in self.all_files_list:
            string = str(file)
            if (substring in string) and (notsubstring not in string):
                list.append(file)
        return list

    def get_proper(self, list):
        """
        Provisional function which tries to find the proper filename from
        very messy data.
        """
        youngest = 0
        thisfile = ""
        for file in list:
            current = to_int(get_date_from_path(file))
            if current > youngest:
                filename = self.cut_extension(file)
                countfiles = 0
                for filee in self.all_files_list:
                    if filename.lower() in filee.lower():
                        countfiles += 1
                if countfiles > 2:
                    youngest = current
                    thisfile = file
        if thisfile == "":
            return None
        else:
            return thisfile

    def get_dual(self, set, param):
        """
        Similar to function above, but concerning the 'dual' files.
        """
        if set is None:
            return None
        if len(set) > 2:
            return "More than 2 files."
        if len(set) == 1:
            if param == "older":
                return set.pop()
            return None
        list = []
        for elem in set:
            list.append(elem)
        if to_int(get_date_from_path(list[0])) > to_int(get_date_from_path(list[1])):
            youngest = list[0]
            oldest = list[1]
        else:
            youngest = list[1]
            oldest = list[0]
        if param == "older":
            return oldest
        elif param == "younger":
            return youngest
        else:
            return "Invalid param."

    def cut_extension(self, file):
        """
        Removes extension from filename.
        """
        if file is None:
            return None
        string = ""
        for char in file:
            if char == '.':
                return string
            else:
                string += char

    def find_file(self, name):
        """
        Finds a full path to file from messy data, having only filename.
        """
        if name is None:
            return None
        for paths, subcatalogs, files in walk(r'.'):
            for file in files:
                if name.lower() in file.lower():
                    return path.join(paths, file)
        return "There is no such file"

class File(object):
    """
    Extracts parameters from one file.
    """

    def __init__(self, path_pre, path_post, users):
        self.user = users
        self.path_pre = self.cut_extension(path_pre)
        self.path_post = self.cut_extension(path_post)
        self.obci_w_pre = self.wii_preprocessing_signal(self.path_pre)
        self.obci_w_post = self.wii_preprocessing_signal(self.path_post)
        if self.obci_w_pre and self.obci_w_post:
            self.obci_markers = get_markers(self.obci_w_pre, self.obci_w_post,
                                            self.user.name, self.user.session_type)
            self.romberg = get_romberg(self.obci_w_pre, self.obci_w_post,
                                       self.user.name, self.user.session_type)
        else:
            self.obci_markers = None
            self.romberg = None

    def cut_extension(self, file):
        if file is None:
            return None
        return ".".join(file.split('.')[:-2])

    def wii_preprocessing_signal(self, file_name):
        """
        Returns ReadManager object of a specific files. Filters the signal
        (33.5 - sampling rate after resampling)
        """
        w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       file_name+'.obci.tag')
        w = wii_filter_signal(w, 33.5/2, 2, use_filtfilt=True)

        return w

def estimate_fs(TSS_samples):
    """
    Function used before resampling, estimates sampling rate of a signal
    by analysing it's timestamp channel.
    """
    durations = []
    for ind in range(1, len(TSS_samples)):
        durations.append(TSS_samples[ind]-TSS_samples[ind-1])
    return 1.0/np.mean(durations)

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

def check_frequencies(USERS):
    """
    Created to check how irregular is data. It was needed to make decision
    about the new sampling rate.
    """

    min_ts = []
    max_ts = []
    lista = []
    for user in USERS:
        user = User(user)
        lista.append([])
        if user.pre_post_file:
            w_pre = get_read_manager(user.pre_post_file.path_pre)
            w_post = get_read_manager(user.pre_post_file.path_post)
            task_stanie, task_oczy, task_bacznosc, task_gabka, task_poznawcze = get_data(w_pre)

            for task in [task_stanie, task_oczy, task_bacznosc, task_gabka, task_poznawcze]:
                maximum = 0
                minimum = 1
                lista_index = 0
                for i in range(1, len(task[2])-1):
                    if (task[2][i] - task[2][i-1]) > maximum:
                        maximum = (task[2][i] - task[2][i-1])
                    if (task[2][i] - task[2][i-1]) < minimum:
                        minimum = (task[2][i] - task[2][i-1])
                    if (task[2][i] - task[2][i-1]) > (1./33.5):
                        lista_index += 1
                min_ts.append(minimum)
                max_ts.append(maximum)
                lista[-1].append(lista_index)
    plt.hist(min_ts, normed=True)
    print(max(max_ts), min(min_ts))
    print(1/max(max_ts), 1/min(min_ts))
    plt.show()
    for i in zip(USERS,lista):
        print(i)

def get_read_manager(file_name):
    """
    Returns WBBReadManager object and creates x and y channels.
    """
    w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       file_name+'.obci.tag')
    w.get_x()
    w.get_y()
    return w

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
    file_tokens = []
    for element in file_list:
        file_tokens.append(decode_token(element))

    USERS = get_users(file_tokens)

    save_data()

