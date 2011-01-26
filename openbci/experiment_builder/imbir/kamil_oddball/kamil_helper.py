#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import csv_manager, random
import csv, copy
from kamil_consts import *
def _multip_groups(groups):
    #get a list of grups, copy every group REPS times
    g = []
    for i in range(REPS):
        curr_g = []
        for group in groups:
            curr_g.append(copy.deepcopy(group))
        random.shuffle(curr_g)
        g += curr_g
    return g
def create_words_file():
    if USE_EXISTING_WORDS_FILE:
        return
    rdr = csv_manager.Reader(RAW_WORDS_FILE, d=',')
    
    #read-in groups
    hdr = rdr.next()
    groups = []
    for i, h in enumerate(hdr):
        groups.append({'group':h, 'words':[]})
    for row in rdr:
        for i, r in enumerate(row):
            groups[i]['words'].append(r)
    rdr.close()
    groups = _multip_groups(groups)
    #add dummy word to every groups
    for g in groups:
        dummy_len = len(g['words'])*DUMMY_WORD_MULT
        g['words'] += [DUMMY_WORD]*dummy_len
        random.shuffle(g['words'])
    
    #create final words file
    wtr = csv_manager.Writer(WORDS_FILE, d=',', q=csv.QUOTE_NONE)
    wtr.write_row(['','',''])
    wtr.write_row(['group', 'word','fix_time'])
    for g in groups:
        for w in g['words']:
            fix = FIX_MIN + random.random()*(FIX_MAX-FIX_MIN)
            grp = g['group']
            wtr.write_row([grp, w, fix])
    wtr.close()
   
   
if USE_SERIAL:
    S = psychopy_serial.SerialSender(PORT_NAME, SERIAL_INIT_VALUE)
    S.open()
    
def send():
    if USE_SERIAL:
        global S
        S.send_next()
#if __name__ == '__main__':
#    create_words_file()