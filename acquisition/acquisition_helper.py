#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os.path
from configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types

def send_finish_saving(conn):
    v = variables_pb2.Variable()
    v.key = 'finish'
    v.value = ''
    conn.send_message(message=v.SerializeToString(), 
                      type=types.SIGNAL_SAVER_CONTROL_MESSAGE,
                      flush=True)

def get_file_path(dir_name, file_name):
    return os.path.expanduser(os.path.normpath(os.path.join(
               os.path.normpath(dir_name), file_name)))
    
