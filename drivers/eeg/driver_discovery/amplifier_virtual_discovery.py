#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

DESC_FILE = 'amplifier_virtual.json'

def driver_available():
	return True

def driver_description():
	with open(DESC_FILE) as f:
		return json.load(f)