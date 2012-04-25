#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
from launcher.launcher_tools import READY_TO_LAUNCH


DESC_FILE = 'amplifier_virtual.json'
_AMP_PEER = 'drivers/eeg/amplifier_virtual.py'
_SCENARIO = 'scenarios/amplifier/virtual_amp_signal.ini'

def driver_descriptions():
    with open(os.path.join(os.path.dirname(__file__), DESC_FILE)) as f:
        desc = {
        		'experiment_info': {
                                "launch_file_path" : _SCENARIO,
                                'experiment_status' :{
                                        'status_name' : READY_TO_LAUNCH
                                }
                                            },
                        'amplifier_peer_info' : {
                                              'path' : _AMP_PEER},
        		'amplifier_params' : {
        								'active_channels' : '',
        								'channel_names' : '',
        								'sampling_rate' : '',
                                                                        'additional_params' : {},
                                                                        'channels_info' : json.load(f)}
        		}
        return [desc]