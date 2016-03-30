#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
import openbci_logging

def get_dummy_context(name):
    d = {'logger': openbci_logging.get_dummy_logger(name)}
    return d

def get_new_context():
    return {}
