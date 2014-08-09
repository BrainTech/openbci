#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
from obci.control.launcher.launcher_tools import READY_TO_LAUNCH
from obci.control.peer.peer_config import PeerConfig
from obci.drivers.eeg.driver_comm import DriverComm


DESC_FILE = 'amplifier_virtual.json'
_AMP_PEER = 'drivers/eeg/amplifier_virtual.py'
_AMP_EXECUTABLE = 'drivers/eeg/cpp_amplifiers/dummy_amplifier'
_SCENARIO = 'scenarios/amplifier/virtual_amp_signal.ini'

def get_description_from_driver():
    conf = PeerConfig('amplifier')
    conf.add_local_param('driver_executable', _AMP_EXECUTABLE)
    conf.add_local_param('samples_per_packet', '4')

    driv = DriverComm(conf, catch_signals=False)
    descr = driv.get_driver_description()
    dic = json.loads(descr)
    driv.terminate_driver()
    return dic

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
                                      'driver_executable' : _AMP_EXECUTABLE,
                                      'path' : _AMP_PEER},
                'amplifier_params' : {
                                                                'active_channels' : '',
                                                                'channel_names' : '',
                                                                'sampling_rate' : '',
                                                                'additional_params' : {},
                                                                'channels_info' : get_description_from_driver()}
                }
        return [desc]
