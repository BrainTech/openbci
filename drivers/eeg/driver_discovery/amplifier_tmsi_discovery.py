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
_USB_DESCS = { 'Porti7' : 'amplifier_porti7_usb.json'}

def _find_bluetooth_amps():
    nearby_devices = bluetooth.discover_devices(lookup_names = True)
    found = []
    for addr, name in nearby_devices:
        is_amp, amp_type = _check_amp_name(name)
        if is_amp:
            found.append((addr, name, amp_type))
    print "AAAAA found:  ", found
    return found


def _find_usb_amps():
    dev_path = os.path.realpath('/dev')
    amps = [dev for dev in os.listdir(dev_path) if\
                dev.startswith('fusbi') or dev.startswith('synfi')]
    amps = [os.path.join(dev_path, dev) for dev in amps]
    amps = [dev for dev in amps if os.readlink(dev).startswith('tmsi')]

    res = [(dev, '', 'Porti7') for dev in amps]
    print "UUUUSSSSSSBBBBBB  ", res
    return res


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
    usb = _find_usb_amps()

    for amp in bt:
        desc = dict(usb_device='', bluetooth_device=amp[0], amplifier_type=amp[2])
        with open(os.path.join(_DESC_BASE_PATH, _BT_DESCS[amp[2]])) as f:
            desc['channels_info'] = json.load(f)
            desc['channels_info']['name'] = amp[1]
        descriptions.append(desc)

    for amp in usb:
        desc = dict(usb_device=amp[0], bluetooth_device='', amplifier_type=amp[2])
        with open(os.path.join(_DESC_BASE_PATH, _USB_DESCS[amp[2]])) as f:
            desc['channels_info'] = json.load(f)
        descriptions.append(desc)

    return descriptions