#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os

from obci.control.launcher.launcher_tools import obci_root,  READY_TO_LAUNCH
from obci.control.peer.peer_config import PeerConfig
from obci.drivers.eeg.driver_comm import DriverComm

_DESC_BASE_PATH = os.path.join(obci_root(), 'drivers/eeg/driver_discovery')

_USB_DESC = 'amplifier_gtec.json'
_AMP_PEER = 'drivers/eeg/c_tmsi_amplifier/amplifier_gtec.py'
_AMP_EXECUTABLE = 'drivers/eeg/cpp_amplifiers/gtec_amplifier'
_SCENARIO = 'scenarios/amplifier/gtec_ekg.ini'


def get_description_from_driver(device_path=None):
    conf = PeerConfig('amplifier')
    conf.add_local_param('driver_executable', 'drivers/eeg/cpp_amplifiers/gtec_amplifier')
    conf.add_local_param('samples_per_packet', '4')

    driv = DriverComm(conf, catch_signals=False)
    descr = driv.get_driver_description()
    try:
        dic = json.loads(descr)
    except ValueError, e:
        print "AMPLIFIER ", device_path, "IS PROBABLY BUSY.", 
        print "Invalid channel description: ", descr
        dic = None

    driv.terminate_driver()
    return dic

def driver_descriptions():
    descriptions = []
    print descriptions

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
                                    
                                    'additional_params' : {},
                                    'active_channels' : '',
                                    'channel_names' : '',
                                    'sampling_rate' : ''},
            }

    chan_inf = None
    try:
        chan_inf = get_description_from_driver()
    except:
        pass
    if chan_inf is None:
        # amplifier busy or an error occurred
        pass
    else:
        desc['amplifier_params']['channels_info'] = chan_inf
        descriptions.append(desc)

    return descriptions
