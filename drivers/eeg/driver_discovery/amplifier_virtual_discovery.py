#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os


DESC_FILE = 'amplifier_virtual.json'
_AMP_PEER = 'drivers/eeg/amplifier_virtual.py'
_SCENARIO = 'scenarios/amplifier/virtual_amp_signal.ini'

def driver_descriptions():
    with open(os.path.join(os.path.dirname(__file__), DESC_FILE)) as f:
        desc = {'channels_info' : json.load(f),
        		'recommended_scenario' : _SCENARIO,
        		'amplifier_peer_path' : _AMP_PEER,
        		'amplifier_params' : {
        								'active_channels' : '',
        								'channel_names' : '',
        								'sampling_rate' : '',
                                                                        'additional_params' : {}}
        		}
        return [desc]