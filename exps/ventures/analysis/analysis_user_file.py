#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from os import *
import pandas as pd
import analysis_helper, analysis_markers
from obci.analysis.balance.wii_preprocessing import *

class User(object):
    """
    Object of this class contains information about one user files.
    Especially, it extracts one path to needed files.
    After arranging data in neat folders, it is no longer as important.
    """

    def __init__(self, name, users_tasks):
        self.name = name.upper()
        print("*** ", self.name, " ***")
        self.complete = False
        self.session_type = users_tasks[users_tasks['ID']==self.name]['session_type'].values[0]
        self.alt_username = users_tasks[users_tasks['ID']==self.name]['alt_ID'].values[0]
        self.all_files_list = self.get_files()
        self.all_files_list = self.remove_duplicate(self.all_files_list)
        self.pretest_files_list = self.one_type_files("pretest", "dual")
        self.postest_files_list = self.one_type_files("post", "dual")
        self.pretest = self.get_proper(self.pretest_files_list)
        self.postest = self.get_proper(self.postest_files_list)
        if self.pretest is not None and self.postest is not None:
            self.complete = True
        self.pretest = analysis_helper.cut_extension(self.pretest)
        self.postest = analysis_helper.cut_extension(self.postest)
        if self.pretest is not None and self.postest is not None:
            self.pre_post_file = File(self.find_file(self.pretest),
                        self.find_file(self.postest), self, users_tasks)
        else:
            self.pre_post_file = None

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
            date_in_string = analysis_helper.get_date_from_path(file)
            current = analysis_helper.date_to_int(date_in_string)
            if current > youngest:
                filename = analysis_helper.cut_extension(file)
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
        first_elem_date_str = \
            analysis_helper.date_to_int(analysis_helper.get_date_from_path(list[0]))
        second_elem_date_str = \
            analysis_helper.date_to_int(analysis_helper.get_date_from_path(list[1]))
        if first_elem_date_str > second_elem_date_str:
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

    def find_file(self, name):
        """
        Finds a full path to file from messy data, having only a filename.
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
    def __init__(self, path_pre, path_post, users, users_tasks):
        self.user = users
        self.path_pre = self.cut_extension(path_pre)
        self.path_post = self.cut_extension(path_post)
        self.obci_w_pre = analysis_helper.get_read_manager(self.path_pre)
        self.obci_w_post = analysis_helper.get_read_manager(self.path_post)
        if self.obci_w_pre and self.obci_w_post:
            self.obci_markers = analysis_markers.get_markers(self.obci_w_pre,
                        self.obci_w_post, self.user.name,
                        self.user.session_type, users_tasks)
            self.romberg = analysis_markers.get_romberg(self.obci_w_pre,
                        self.obci_w_post, self.user.name,
                        self.user.session_type, users_tasks)
        else:
            self.obci_markers = None
            self.romberg = None

    def cut_extension(self, file):
        if file is None:
            return None
        return ".".join(file.split('.')[:-2])

def get_data_fragment(wbb_mgr, start_tag, end_tag):
    data = wii_cut_fragments(wbb_mgr, start_tag_name=start_tag,
                             end_tags_names=[end_tag], TS=True)
    x, y = analysis_helper.remove_baseline(data)
    return x, y

def get_data(wbb_mgr):
    """
    Returns specific fragments of signal.
    """
    task_stanie = get_data_fragment(wbb_mgr, 'ss_start', 'ss_stop')
    task_oczy = get_data_fragment(wbb_mgr, 'ss_oczy_start', 'ss_oczy_stop')
    task_bacznosc = get_data_fragment(wbb_mgr, 'ss_bacznosc_start',
                                      'ss_bacznosc_stop')
    task_gabka = get_data_fragment(wbb_mgr, 'ss_gabka_start', 'ss_gabka_stop')
    task_poznawcze = get_data_fragment(wbb_mgr, 'ss_poznawcze_start',
                                       'ss_poznawcze_stop')
    return task_stanie, task_oczy, task_bacznosc, task_gabka, task_poznawcze

def get_dual_data_fragments(wbb_mgr):
    """
    Returns specific fragments of signal.
    """
    task_stanie_zgodny1 = get_data_fragment(wbb_mgr, 'ss_zgodny1_start',
                                            'ss_zgodny1_stop')
    task_stanie_zgodny2 = get_data_fragment(wbb_mgr, 'ss_zgodny2_start',
                                            'ss_zgodny2_stop')
    task_stanie_niezgodny1 = get_data_fragment(wbb_mgr, 'ss_niezgodny1_start',
                                            'ss_niezgodny1_stop')
    task_stanie_niezgodny2 = get_data_fragment(wbb_mgr, 'ss_niezgodny2_start',
                                            'ss_niezgodny2_stop')

    task_bacznosc_zgodny1 = get_data_fragment(wbb_mgr, 'ss_bacznosc_zgodny1_start',
                                            'ss_bacznosc_zgodny1_stop')
    task_bacznosc_zgodny2 = get_data_fragment(wbb_mgr, 'ss_bacznosc_zgodny2_start',
                                            'ss_bacznosc_zgodny2_stop')
    task_bacznosc_niezgodny1 = get_data_fragment(wbb_mgr, 'ss_bacznosc_niezgodny1_start',
                                            'ss_bacznosc_niezgodny1_stop')
    task_bacznosc_niezgodny2 = get_data_fragment(wbb_mgr, 'ss_bacznosc_niezgodny2_start',
                                            'ss_bacznosc_niezgodny2_stop')

    task_gabka_zgodny1 = get_data_fragment(wbb_mgr, 'ss_gabka_zgodny1_start',
                                            'ss_gabka_zgodny1_stop')
    task_gabka_zgodny2 = get_data_fragment(wbb_mgr, 'ss_gabka_zgodny2_start',
                                            'ss_gabka_zgodny2_stop')
    task_gabka_niezgodny1 = get_data_fragment(wbb_mgr, 'ss_gabka_niezgodny1_start',
                                            'ss_gabka_niezgodny1_stop')
    task_gabka_niezgodny2 = get_data_fragment(wbb_mgr, 'ss_gabka_niezgodny2_start',
                                            'ss_gabka_niezgodny2_stop')

    return task_stanie_zgodny1, task_stanie_zgodny2, task_stanie_niezgodny1, task_stanie_niezgodny2, \
           task_bacznosc_zgodny1, task_bacznosc_zgodny2, task_bacznosc_niezgodny1, task_bacznosc_niezgodny2, \
           task_gabka_zgodny1, task_gabka_zgodny2, task_gabka_niezgodny1, task_gabka_niezgodny2

def get_short_data(wbb_mgr):
    """
    Returns data fragments corresponding to single task in dual files.
    results[2:13] - ss_zgodny1
    results[16:27] - ss_niezgodny1
    results[30:41] - ss_zgodny2
    results[44:55] - ss_niezgodny2

    results[60:71] - ss_bacznosc_zgodny1
    results[74:85] - ...
    results[88:99]
    results[102:113]

    results[118:129]
    results[132:143]
    results[146:157]
    results[160:171]
    """
    results = []
    tags = wbb_mgr.mgr.get_tags()
    previous_tag = 0
    for tag in tags:
        if previous_tag:

            fragment = wii_cut_fragments(wbb_mgr, start_tag_name=previous_tag['name'],
                                         end_tags_names=[tag['name']], TS=True)
            results.append(fragment)
        previous_tag = tag
    return results

def user_task_checker(user, task, users_data):
    """
    Checks if a fragment of one user's data is marked as good enough for
    analysis (check users_task.csv file in folder '/data/').
    """
    if int(users_data[users_data['ID'] == user][task].values[0]):
        return True
    else:
        return False

def get_session_type(name):
    """
    Checks in users.csv (in folder named 'data', provide a proper path!)
    which type of session this user was performing.
    """
    data = pd.read_csv('../data/users.csv', index_col=0, dtype='str')
    if name in data['ID'].values:
        return data[data['ID']==name]['session_type'].values[0]
    else:
        return None