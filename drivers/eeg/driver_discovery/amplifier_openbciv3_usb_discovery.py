#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os

from obci.control.launcher.launcher_tools import obci_root,  READY_TO_LAUNCH
from obci.control.peer.peer_config import PeerConfig
from obci.drivers.eeg.driver_comm import DriverComm
from obci.drivers.eeg.openbciv3 import openbciv3

_AMP_PEER = 'drivers/eeg/amplifier_openbciv3_peer.py'
_AMP_EXECUTABLE = 'drivers/eeg/cpp_amplifiers/tmsi_amplifier'
_SCENARIO = 'scenarios/amplifier/openbciv3_dummy.ini'


def _find_usb_amps():
    dev_path = os.path.realpath('/dev')
    amps = [dev for dev in os.listdir(dev_path) if\
                dev.startswith('fusbi')]
    amps = [os.path.join(dev_path, dev) for dev in amps]
    amps = [(dev, '', 'Porti7') for dev in amps if os.readlink(dev).startswith('tmsi')]
    return [('/dev/usb0','','nazwa')]

def get_description_from_driver(driver):
    descr = {"channels": driver.get_channels_info(), 
             "physical_channels": driver.get_channels_count(),
             "sampling_rates": driver.get_sampling_rates(),
             "name": driver.get_name()
	    }

    return descr

def driver_descriptions():
    driver = openbciv3.OpenBCIBoard()

    descriptions = []
    usb = _find_usb_amps()

    for amp in usb:

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
                                        
                                        'additional_params' : {'usb_device' : '',
                                                                'bluetooth_device' : ''},
                                        'active_channels' : '',
                                        'channel_names' : '',
                                        'sampling_rate' : ''},
                }

        desc['amplifier_params']['additional_params']['usb_device'] = amp[0]
        desc['amplifier_params']['channels_info'] = get_description_from_driver(driver)
        descriptions.append(desc)

    return descriptions
