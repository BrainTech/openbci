#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

from obci.control.launcher.obci_script import OBCIArgParser

def run():
    cmd_mgr = OBCIArgParser()
    cmd_mgr.setup_commands()
    args = cmd_mgr.parser.parse_args()
    args.func(args)

