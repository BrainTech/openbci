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

def get_file_name(search_name, search_dir):
    search_dir  = os.path.expanduser(search_dir)  
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

def get_users(file_list):
    """
    Extracts user names from list of tokens created from given file list.
    """
    file_tokens = []
    for element in file_list:
        file_tokens.append(decode_token(element))
    users_list = []
    for elem in file_list:
        if (elem[0].upper() not in users_list) and (len(elem[0]) == 4) \
                and (elem[0][2].isdigit()):
            users_list.append(elem[0].upper())
    return users_list

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

