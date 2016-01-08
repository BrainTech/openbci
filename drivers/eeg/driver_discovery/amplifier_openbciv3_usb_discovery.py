#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import glob

from obci.control.launcher.launcher_tools import obci_root, READY_TO_LAUNCH
from obci.control.peer.peer_config import PeerConfig
from obci.drivers.eeg.driver_comm import DriverComm
from obci.drivers.eeg.openbciv3 import openbciv3

_AMP_PEER = 'drivers/eeg/amplifier_openbciv3_peer.py'
_SCENARIO = 'scenarios/amplifier/openbciv3.ini'


def _find_usb_amps():
    return glob.glob('/dev/ttyUSB[0-9]*')

def driver_descriptions():
    driver = openbciv3.OpenBCIBoard()
    descriptions = []

    for amp in _find_usb_amps():
        desc = {
            'experiment_info': {
                'launch_file_path': _SCENARIO,
                'experiment_status': {
                    'status_name': READY_TO_LAUNCH
                }
            },
            'amplifier_peer_info': {
                'path': _AMP_PEER
            },
            'amplifier_params': {                                        
                'additional_params': {
                    'usb_device': amp,
                    'bluetooth_device': ''
                },
                'active_channels': '',
                'channel_names': '',
                'sampling_rate': '',
                'channels_info': {
                    'channels': driver.get_channels_info(), 
                    'physical_channels': driver.get_channels_count(),
                    'sampling_rates': driver.get_sampling_rates(),
                    'name': driver.get_name()
                }
            }
        }
        descriptions.append(desc)

    return descriptions

