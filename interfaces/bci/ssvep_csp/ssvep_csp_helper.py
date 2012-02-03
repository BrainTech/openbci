#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from interfaces import interfaces_logging as logger
LOGGER = logger.get_logger("ssvep_csp_helper")

from acquisition import acquisition_helper
import pickle

def get_csp_config(path, name):
    file_name = acquisition_helper.get_file_path(path, name)
    csp_file = file_name+'.csp'
    f = open(csp_file, 'r')
    d = pickle.load(f)
    f.close()
    LOGGER.info("Got csp config:")
    LOGGER.info(str(d))
    return d
