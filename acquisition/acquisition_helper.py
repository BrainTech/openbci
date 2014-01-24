#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os.path
from multiplexer.multiplexer_constants import types
from obci.acquisition import acquisition_control
from obci.control.launcher.launcher_tools import obci_root

def send_finish_saving(conn):
    conn.send_message(message='finish',
                      type=types.ACQUISITION_CONTROL_MESSAGE,
                      flush=True)

def finish_saving(mx_addresses=None):
    if mx_addresses is None:
        return acquisition_control.finish_saving()
    else:
        return acquisition_control.finish_saving(mx_addresses)

def get_file_path(dir_name, file_name):
    if not os.path.isabs(os.path.expanduser(dir_name)) and len(dir_name) != 0:
        dir_name = os.path.normpath(os.path.join(obci_root(), dir_name))
    return os.path.expanduser(os.path.normpath(os.path.join(os.path.normpath(dir_name), file_name)))
