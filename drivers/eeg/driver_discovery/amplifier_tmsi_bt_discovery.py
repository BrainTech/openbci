#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import bluetooth
import os

from launcher.launcher_tools import obci_root

_DESC_BASE_PATH = os.path.join(obci_root(), 'drivers/eeg/driver_discovery')

_TYPES = ['Porti7', 'MobiMini', 'Mobi5']
_BT_DESCS = {
                'Porti7' : 'amplifier_porti7_bluetooth.json',
                'MobiMini' : 'amplifier_mobimini.json',
                'Mobi5' : 'amplifier_mobi5.json'
            }
_AMP_PEER = 'drivers/eeg/c_tmsi_amplifier/amplifier_tmsi.py'
_SCENARIO = 'scenarios/amplifier/tmsi_amp_signal.ini'

def _find_bluetooth_amps():
    try:
        nearby_devices = bluetooth.discover_devices(duration=3, lookup_names = True)
    except bluetooth.BluetoothError, e:
        print "ERROR:  ", str(e)
        nearby_devices = []

    found = []
    for addr, name in nearby_devices:
        is_amp, amp_type = _check_amp_name(name)
        if is_amp:
            found.append((addr, name, amp_type))
    print "Found bluetooth devices: ", found
    return found

def _check_amp_name(name):
    amp_type = ''
    for type_ in _TYPES:
        if name.startswith(type_):
            amp_type = type_

    name_ok = False
    parts = name.split()
    if len(parts) == 2:
        try:
            n = int(parts[1])
        except Exception, e:
            pass
        else:
            name_ok = amp_type != ''
    return name_ok, amp_type


def driver_descriptions():
    descriptions = []
    bt = _find_bluetooth_amps()
    desc = {
                'recommended_scenario' : _SCENARIO,
                'amplifier_peer_path' : _AMP_PEER,
                'amplifier_params' : {
                                        
                                        'additional_params' : {'usb_device' : '',
                                                                'bluetooth_device' : ''},
                                        'active_channels' : '',
                                        'channel_names' : '',
                                        'sampling_rate' : ''},
                }
    for amp in bt:
        desc['amplifier_params']['bluetooth_device'] = amp[0]
        with open(os.path.join(_DESC_BASE_PATH, _BT_DESCS[amp[2]])) as f:
            desc['channels_info'] = json.load(f)
            desc['channels_info']['name'] = amp[1]
        descriptions.append(desc)

    return descriptions