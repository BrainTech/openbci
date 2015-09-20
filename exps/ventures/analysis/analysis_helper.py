# -*- coding: utf-8 -*-
#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Anna Chabuda <anna.chabuda@gmail.com>
#     Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from obci.analysis.balance.wii_read_manager import WBBReadManager
import glob
import os.path
import pandas as pd
from os import *
import analysis_user_file

def get_file_name(search_name, search_dir):
    search_dir = os.path.expanduser(search_dir)
    files = glob.glob(('{}/{}').format(search_dir, search_name))
    for file_ in files:
        yield file_

def set_first_timestamp(mgr):
    first_timestamp = float(mgr.get_param('first_sample_timestamp'))
    for tag in mgr.get_tags():
        tag['start_timestamp'] -= first_timestamp
        tag['end_timestamp'] -= first_timestamp 
    return mgr

def get_read_manager(file_name, get_data_channels=False, filter=True):
    """
    Returns WBBReadManager object and creates x and y channels.
    """
    w = WBBReadManager(file_name+'.obci.xml',
                       file_name+'.obci.raw',
                       file_name+'.obci.tag')
    if get_data_channels:
        w.get_x()
        w.get_y()
    if filter:
        w = wii_filter_signal(w, 33.5/2, 2, use_filtfilt=True)
    return w

def decode_token(path):
    """
    Extracts tokens form given file path.
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

def get_users():
    """
    Extracts user names from list of tokens created from given file list.
    """
    data = pd.read_csv('~/data/users_tasks.csv', index_col=0, dtype='str')
    return data['ID'].values

def get_users_as_objects(users_names):
    users = []
    for user in users_names:
        user_object = analysis_user_file.User(user)
        users.append(user_object)

def get_date_from_path(file):
    """
    For specific files, extracts date from file as a string.
    """
    file = str(file)
    for i in range(0, len(file)-3):
        if file[i:i+3] == "201":
            return file[i:i+19]

def date_to_int(date):
    """
    Changes given date from string to integer.
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

def get_file_list(path):
    """
    :return: List of files in specified path.
    """
    file_list = []
    for paths, subcatalogs, files in walk(r'./'+path):
        for file in files:
            if 'resampled' in file and 'psy' not in file and 'adjust' not in file:
                file = cut_extension(file)
                file_list.append(path.join(paths, file))
    return file_list

def cut_extension(file):
    if file is None:
        return None
    string = file[0]
    for char in range(1, len(file)):
        if file[char] == '.':
            return string
        else:
            string += file[char]

def average(data):
    """
    For each columns of type 'zgodny1', 'zgodny2' transforms them into
    one column 'zgodny', with values being mean from previous ones.
    """
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

def remove_baseline(t):
    """
    Returns x and y data, counts its baseline (mean from first tenth part
    of signal) and cuts it off.
    """
    x_baseline = t[0][0:(len(t[0])/10)]
    y_baseline = t[1][0:(len(t[1])/10)]
    x_baseline = sum(x_baseline)/len(x_baseline)
    y_baseline = sum(y_baseline)/len(y_baseline)
    x = t[0][(len(t[0])/10):]
    x = (x - x_baseline)*22.5
    y = t[1][(len(t[1])/10):]
    y = (y - y_baseline)*13
    return x, y
