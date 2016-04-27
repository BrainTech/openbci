#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

def run(data, config, channel_names, first_sample_timestampm, fs):
    print "Analysis run..."

    config = {'param1': 0, 
              'param2': 1}
    time.sleep(10)
    
    print "Analysis finish..."
    return config