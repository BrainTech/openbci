#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from obci.configs import settings

USERS='users.csv'
BASELINE_RESULTS='baseline_results.csv'
CALIBRATION_RESULTS='calibration_results.csv'
GAME_RESULTS = 'game_results.csv'


TIME_STR = '20%y-%m-%d_%H-%M-%S'
def current_time_to_string():
    """Return current time in TIME_STR format as string"""
    return time.strftime(TIME_STR)

def time_from_string(t):
    """For given time in string format TIME_STR
    return time in system timestamps (seconds)"""
    return time.mktime(time.strptime(t, TIME_STR))

def baseline_set(user_id, xa,ya,xb,yb,xc,yc, file_name):
    #add to csv:user_id, xa,ya,xb,yb,xc,yc, file_name, current_time_to_string()
    pass

def baseline_get_last(user_id):
    t = '2015-01-16_09-09-25'
    xa=1.0
    ya=1.0
    xb=0.0
    yb=0.0
    xc=0.1
    yc=0.1
    return xa,ya,xb,yb,xc,yc,t #or None

def calibration_set(user_id, up, right, down, left, file_name):
    #add to csv user_id, up, right, down, left, file_name, current_time_to_string()
    pass

def calibration_get_last(user_id):
    t = '2015-01-16_09-09-25'
    up = 1.0
    right = 1.0
    down = 0.1
    left= 1.0
    return up, right, down, left, t
