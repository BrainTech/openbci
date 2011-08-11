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
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
#

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
from azouk._allinone import OperationFailed
import settings, variables_pb2
from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("configurer", 'info')
import time


class Configurer(object):
    def __init__(self, addresses):
        self.addresses = addresses

    def get_configs(self, config_keys):
        LOGGER.info("Start initializing configurer ...")
        connection = connect_client(type = peers.CONFIGURER, addresses=self.addresses)
        configs = {}
        LOGGER.info("Start getting  configs...")
        for key in config_keys:
            config = ""
            while len(config) == 0:
                LOGGER.info("Waiting for config "+key+" ...")
                try:
                    config = connection.query(
                        message=key, 
                        type=types.DICT_GET_REQUEST_MESSAGE).message
                except OperationFailed:
                    LOGGER.info("It seems hashtable is down... Try again...")
                time.sleep(0.5)
            configs[key] = config
            LOGGER.info("Got config: "+str(key)+" as: "+str(configs[key]))

        LOGGER.info("Got all configs...")
        connection.shutdown()
        return configs

    def set_configs(self, configs, connection=None):
        if connection is None:
            l_connection = connect_client(type = peers.CONFIGURER, addresses=self.addresses)
        else:
            l_connection = connection

        for key, value in configs.iteritems():
            l_var = variables_pb2.Variable()
            l_var.key = key
            l_var.value = value
            l_connection.send_message(message = l_var.SerializeToString(), 
                                      type = types.DICT_SET_MESSAGE, flush=True)

        if connection is None:
            l_connection.shutdown()
            

if __name__ == "__main__":
    Configurer(settings.MULTIPLEXER_ADDRESSES, ['NumOfChannels'])
