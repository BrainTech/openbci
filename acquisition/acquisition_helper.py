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

def finish_saving(mx_addresses=None, s_types=['eeg']):
    if mx_addresses is None:
        return acquisition_control.finish_saving(s_types=s_types)
    else:
        return acquisition_control.finish_saving(s_types=s_types, mx_addresses=mx_addresses)

def wait_saving_finished(mx_addresses=None, s_types=['eeg']):
    if mx_addresses is None:
        return acquisition_control.wait_saving_finished(s_types=s_types)
    else:
        return acquisition_control.wait_saving_finished(s_types=s_types, mx_addresses=mx_addresses)


def get_file_path(dir_name, file_name):
    if not os.path.isabs(os.path.expanduser(dir_name)) and len(dir_name) != 0:
        dir_name = os.path.normpath(os.path.join(obci_root(), dir_name))
    return os.path.expanduser(os.path.normpath(os.path.join(os.path.normpath(dir_name), file_name)))


def get_acquisition_peers(amplifier_type='amplifier'):
    if amplifier_type == 'amplifier':
        return [
            {'peer_type':'signal',
             'peer_name': "signal_saver",
             'peer_path': "acquisition/signal_saver_peer.py"},
            {'peer_type': 'tag',
             'peer_name': "tag_saver",
             'peer_path': "acquisition/tag_saver_peer.py"},
            {'peer_type':'info',
             'peer_name': "info_saver",
             'peer_path': "acquisition/info_saver_peer.py"}
        ]

    elif amplifier_type == 'wii_amplifier':
        return [
            {'peer_type':'signal',
             'peer_name': "wii_signal_saver",
             'peer_path': "acquisition/wii_board_saver_peer.py"},
            {'peer_type': 'tag',
             'peer_name': "wii_tag_saver",
             'peer_path': "acquisition/wii_board_tag_saver_peer.py"},
            {'peer_type':'info',
             'peer_name': "wii_info_saver",
             'peer_path': "acquisition/wii_board_info_saver_peer.py"}
        ]

