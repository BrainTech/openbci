#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os


DESC_FILE = 'amplifier_virtual.json'

def driver_descriptions():
    with open(os.path.join(os.path.dirname(__file__), DESC_FILE)) as f:
        desc = {'channels_info' : json.load(f)}
        return [desc]