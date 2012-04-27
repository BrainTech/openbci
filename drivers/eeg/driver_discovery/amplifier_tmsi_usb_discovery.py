#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import bluetooth
import os

from launcher.launcher_tools import obci_root,  READY_TO_LAUNCH

_DESC_BASE_PATH = os.path.join(obci_root(), 'drivers/eeg/driver_discovery')

_TYPES = ['Porti7']

_USB_DESCS = { 'Porti7' : 'amplifier_porti7_usb.json',
                'SynFi' : 'amplifier_tmsi_synfi.json'}
_AMP_PEER = 'drivers/eeg/c_tmsi_amplifier/amplifier_tmsi.py'
_SCENARIO = 'scenarios/amplifier/tmsi_amp_signal.ini'


def _find_usb_amps():
    dev_path = os.path.realpath('/dev')
    amps = [dev for dev in os.listdir(dev_path) if\
                dev.startswith('fusbi')]

    synfi_amps = [dev for dev in os.listdir(dev_path) if\
                dev.startswith('synfi')]
    amps = [os.path.join(dev_path, dev) for dev in amps]
    synfi_amps = [os.path.join(dev_path, dev) for dev in synfi_amps]
    amps = [(dev, '', 'Porti7') for dev in amps if os.readlink(dev).startswith('tmsi')]
    synfi_amps = [(dev, '', 'SynFi') for dev in synfi_amps if os.readlink(dev).startswith('tmsi')]
    amps += synfi_amps

    print "Found USB devices: ", amps
    return amps


def driver_descriptions():
    descriptions = []
    usb = _find_usb_amps()
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
                                        
                                        'additional_params' : {'usb_device' : '',
                                                                'bluetooth_device' : ''},
                                        'active_channels' : '',
                                        'channel_names' : '',
                                        'sampling_rate' : ''},
                }

    for amp in usb:
        desc['amplifier_params']['additional_params']['usb_device'] = amp[0]
        with open(os.path.join(_DESC_BASE_PATH, _USB_DESCS[amp[2]])) as f:
            desc['amplifier_params']['channels_info'] = json.load(f)
        descriptions.append(desc)

    return descriptions