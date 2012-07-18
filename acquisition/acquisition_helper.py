#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os.path
from obci_configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from acquisition import acquisition_control

def send_finish_saving(conn):
    conn.send_message(message='finish',
                      type=types.ACQUISITION_CONTROL_MESSAGE,
                      flush=True)

def finish_saving():
    return acquisition_control.finish_saving()

def get_file_path(dir_name, file_name):
    return os.path.expanduser(os.path.normpath(os.path.join(
               os.path.normpath(dir_name), file_name)))
    
