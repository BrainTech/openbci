#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#     Joanna Tustanowska <joanna.tustanowska@titanis.pl>

"""Module defines a single method get_logger that returns logger with
set logging level. Change logging.INFO lines to change logging level."""
import os
import logging
import logging.handlers
import log_mx_handler
import common.net_tools as net

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


MAX_FILE_SIZE_B = 1000000
LOG_BUFFER_SIZE_B = 5000
BACKUP_COUNT = 2

def log_formatter():
    """Standard openBCI log formatter"""
    return logging.Formatter(
                    "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s")

def get_logger(name, file_level='debug', stream_level='warning', 
                            mx_level='warning', conn=None, log_dir=None):
    """Return logger with name as name. And logging level p_level.
    p_level should be in (starting with the most talkactive):
    'debug', 'info', 'warning', 'error', 'critical'."""
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        # Some module migh be imported few times. In every get_logger call 
        # with name = "X" we return the same instance of logger, bu we must
        # ensure, that the logger has no more than one handler.
        
        level = LEVELS['debug']
        logger.setLevel(level)
        formatter = log_formatter()

        shandler = logging.StreamHandler()
        shandler.setFormatter(formatter)
        shandler.setLevel(LEVELS[stream_level])
        logger.addHandler(shandler)
        
        if conn is not None:
            mxhandler = log_mx_handler.LogMXHandler(conn)
            mxhandler.setLevel(LEVELS[mx_level])
            logger.addHandler(mxhandler)

        if log_dir is not None:
            fhandler = logging.handlers.RotatingFileHandler(
                                    os.path.join(log_dir, name + ".log"), 
                                    maxBytes=MAX_FILE_SIZE_B,
                                    backupCount=BACKUP_COUNT)
            fhandler.setFormatter(formatter)
            fhandler.setLevel(LEVELS[file_level])
            # memhandler = logging.handlers.MemoryHandler(LOG_BUFFER_SIZE_B, 
            #                                     flushLevel=LEVELS['warning'],
            #                                            target=fhandler)
            # memhandler.setLevel(LEVELS file_level])
            logger.addHandler(fhandler)

    return logger
