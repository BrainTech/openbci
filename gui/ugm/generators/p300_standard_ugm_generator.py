#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, copy
from configs import settings, variables_pb2

from gui.ugm import ugm_config_manager

def run(input, output, rows, cols):
    mgr = ugm_config_manager.UgmConfigManager(input)
    fields = mgr.get_ugm_fields()
    stims = fields[1]['stimuluses']
    stim = stims[0]
    stims[:] = []

    width = 1/float(cols)
    height = 1/float(rows)
    
    id1 = int(stim['id'])
    id2 = int(stim['stimuluses'][0]['id'])    
    id3 = int(stim['stimuluses'][0]['stimuluses'][0]['id'])
    for i in range(rows):
        for j in range(cols):
            #set outside rectangular
            s1 = copy.deepcopy(stim)
            s1['id'] = id1
            s1['width'] = width
            s1['height'] = height
            s1['position_horizontal'] = j*width
            s1['position_vertical'] = i*height

            #set inside rectangular
            s2 = s1['stimuluses'][0]
            s2['id'] = id2
            s2['width_type'] = 'relative'
            s2['height_type'] = 'relative'
            s2['width'] = 1.0
            s2['height'] = 1.0

            #set text stimulus
            s3 = s2['stimuluses'][0]
            s3['id'] = id3
            s3['message'] = 'B'


            stims.append(s1)
            id1 += 1
            id2 += 1
            id3 += 1

    mgr.set_full_config(fields)
    mgr.update_to_file(output, True)

if __name__ == '__main__':
    try:
        out = sys.argv[1]
        rows = sys.argv[2] 
        cols = sys.argv[3]
    except:
        out = 'p300_classic_7x7'
        rows = 7
        cols = 7
    run('p300_base2', out, rows, cols)
