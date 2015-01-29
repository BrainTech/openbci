#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from obci.configs import settings
from obci.acquisition import acquisition_helper
import pandas as pd

import os.path

USERS='users.csv'
BASELINE_RESULTS='baseline_results.csv'
CALIBRATION_RESULTS='calibration_results.csv'
GAME_RESULTS = 'game_results.csv'
GAME_WII_RESULTS = 'game_wii_results.csv'


TIME_STR = '20%y-%m-%d_%H-%M-%S'

def col_mame_to_save_get(data, names_in_cols):
    max_number = max([int(value) for value in data['number'].values])
    cols =  sum([['{}_{}'.format(ind, name) for name in names_in_cols] for ind in range(1, max_number+1)], [])
    return sum([['ID', 'number'], cols], [])

def get_database_file_name(file_name):
    dir_name = os.path.join(settings.MAIN_DIR, 'exps/ventures/data')
    return acquisition_helper.get_file_path(dir_name, file_name)

def session_type_get(user_id):
    data = pd.read_csv(get_database_file_name(USERS), index_col=0, dtype='str')
    return data[data['ID']==user_id]['session_type'].values[0]

def session_number_get(user_id):
    data = pd.read_csv(get_database_file_name(GAME_RESULTS), index_col=0, dtype='str')
    if user_id in data['ID'].values:
        number = int(data[data['ID']==user_id]['number'].values[0])
        return number+1
    else:
        return 1

def current_time_to_string():
    """Return current time in TIME_STR format as string"""
    return time.strftime(TIME_STR)

def time_from_string(t):
    """For given time in string format TIME_STR
    return time in system timestamps (seconds)"""
    return time.mktime(time.strptime(t, TIME_STR))

def baseline_set(user_id, xa,ya,xb,yb,xc,yc, file_name):
    data = pd.read_csv(get_database_file_name(BASELINE_RESULTS), index_col=0, dtype='str')
    if user_id in data['ID'].values:
        number = int(data[data['ID']==user_id]['number'].values[0])+1
        data.set_value(data[data['ID']==user_id].index[0], 'number', str(number))
    else:
        data_user = pd.DataFrame()
        number = '1'
        data_user['ID'] = pd.Series(user_id)
        data_user['number']=pd.Series(number)
        data = data.append(data_user)
        data = data.set_index([range(0, len(data.values))])

    data.set_value(data[data['ID']==user_id].index[0], '{}_xa'.format(number), xa.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_ya'.format(number), ya.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_xb'.format(number), xb.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_yb'.format(number), yb.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_xc'.format(number), xc.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_yc'.format(number), yc.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_file_name'.format(number), file_name)
    data.set_value(data[data['ID']==user_id].index[0], '{}_time'.format(number), current_time_to_string())
    
    data.to_csv(get_database_file_name(BASELINE_RESULTS), 
                                       cols=col_mame_to_save_get(data, ['xa','ya','xb','yb','xc','yc','file_name','time']))

def baseline_get_last(user_id):
    data = pd.read_csv(get_database_file_name(BASELINE_RESULTS), index_col=0,  dtype='str')
    if user_id in data['ID'].values:
        number = data[data['ID']==user_id]['number'].values[0]
        xa = data[data['ID']==user_id]['{}_xa'.format(number)].values[0]
        ya = data[data['ID']==user_id]['{}_ya'.format(number)].values[0]
        xb = data[data['ID']==user_id]['{}_xb'.format(number)].values[0]
        yb = data[data['ID']==user_id]['{}_yb'.format(number)].values[0]
        xc = data[data['ID']==user_id]['{}_xc'.format(number)].values[0]
        yc = data[data['ID']==user_id]['{}_yc'.format(number)].values[0]
        t = data[data['ID']==user_id]['{}_time'.format(number)].values[0]
        return (xa, ya, xb, yb, xc, yc, t) 
    else:
        return None

def calibration_set(user_id, up, right, down, left, file_name):
    data = pd.read_csv(get_database_file_name(CALIBRATION_RESULTS), index_col=0, dtype='str')
    if user_id in data['ID'].values:
        number = int(data[data['ID']==user_id]['number'].values[0])+1
        data.set_value(data[data['ID']==user_id].index[0], 'number', str(number))
    else:
        data_user = pd.DataFrame()
        number = '1'
        data_user['ID'] = pd.Series(user_id)
        data_user['number']=pd.Series(number)
        data = data.append(data_user)
        data = data.set_index([range(0, len(data.values))])

    data.set_value(data[data['ID']==user_id].index[0], '{}_up'.format(number), up.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_down'.format(number), down.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_left'.format(number), left.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_right'.format(number), right.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_time'.format(number), current_time_to_string())
    data.to_csv(get_database_file_name(CALIBRATION_RESULTS),
                cols=col_mame_to_save_get(data, ['up','down','left','right','time'])) 

def calibration_get_last(user_id):
    data = pd.read_csv(get_database_file_name(CALIBRATION_RESULTS), index_col=0,  dtype='str')
    if user_id in data['ID'].values:
        number = data[data['ID']==user_id]['number'].values[0]
        up = data[data['ID']==user_id]['{}_up'.format(number)].values[0]
        down = data[data['ID']==user_id]['{}_down'.format(number)].values[0]
        left = data[data['ID']==user_id]['{}_left'.format(number)].values[0]
        right = data[data['ID']==user_id]['{}_right'.format(number)].values[0]
        t = data[data['ID']==user_id]['{}_time'.format(number)].values[0]
        return (up, right, down, left, t) 
    else:
        return None

def wii_current_level_set(user_id, level):
    data = pd.read_csv(get_database_file_name(GAME_WII_RESULTS), index_col=0, dtype='str')
    if user_id in data['ID'].values:
        number = int(data[data['ID']==user_id]['number'].values[0])+1
        data.set_value(data[data['ID']==user_id].index[0], 'number', str(number))
    else:
        data_user = pd.DataFrame()
        number = '1'
        data_user['ID'] = pd.Series(user_id)
        data_user['number']=pd.Series(number)
        data = data.append(data_user)
        data = data.set_index([range(0, len(data.values))])

    data.set_value(data[data['ID']==user_id].index[0], '{}_level'.format(number), level.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_time'.format(number), current_time_to_string())
    data.to_csv(get_database_file_name(GAME_WII_RESULTS), 
                                       cols=col_mame_to_save_get(data, ['level','time']))     

def wii_current_level_get_last(user_id):
    data = pd.read_csv(get_database_file_name(GAME_WII_RESULTS), index_col=0,  dtype='str')
    if user_id in data['ID'].values:
        number = data[data['ID']==user_id]['number'].values[0]
        level = data[data['ID']==user_id]['{}_level'.format(number)].values[0]
        return int(level)
    else:
        return 1

def maze_current_level_set(user_id, level):
    data = pd.read_csv(get_database_file_name(GAME_RESULTS), index_col=0, dtype='str')
    if user_id in data['ID'].values:
        number = int(data[data['ID']==user_id]['number'].values[0])+1
        data.set_value(data[data['ID']==user_id].index[0], 'number', str(number))
    else:
        data_user = pd.DataFrame()
        number = '1'
        data_user['ID'] = pd.Series(user_id)
        data_user['number']=pd.Series(number)
        data = data.append(data_user)
        data = data.set_index([range(0, len(data.values))])

    data.set_value(data[data['ID']==user_id].index[0], '{}_level'.format(number), level.__repr__())
    data.set_value(data[data['ID']==user_id].index[0], '{}_time'.format(number), current_time_to_string())
    data.to_csv(get_database_file_name(GAME_RESULTS),
                cols=col_mame_to_save_get(data, ['level', 'time']))   

def maze_current_level_get_last(user_id):
    data = pd.read_csv(get_database_file_name(GAME_RESULTS), index_col=0,  dtype='str')
    if user_id in data['ID'].values:
        number = data[data['ID']==user_id]['number'].values[0]
        level = data[data['ID']==user_id]['{}_level'.format(number)].values[0]
        return int(level)
    else:
        return 1


