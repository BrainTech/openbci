#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates, error_codes
from obci_control_peer import OBCIControlPeer, basic_arg_parser

import common.obci_control_settings as settings

class OBCIClient(OBCIControlPeer):
	pass