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

"""Current script is supposed to be fired if you want to run 
ugm as a part of openbci (with multiplexer and all that stuff)."""
import socket, thread
import os, os.path, sys


from ugm import ugm_config_manager
from ugm import ugm_server

from tags import tagger
import ugm_logging as logger
import settings


BUF = 2**19

LOGGER = logger.get_logger('run_ugm')

import variables_pb2, settings, random, time


class UdpServer(object):
    """The class solves a problem with PyQt - it`s main window MUST be 
    created in the main thread. As a result I just can`t fire multiplexer
    and fire ugm_engine in a separate thread because it won`t work. I can`t
    fire ugm_engine and then fire multiplexer in a separate thread as 
    then multiplexer won`t work ... To solve this i fire ugm_engine in the 
    main thread, fire multiplexer in separate PROCESS and create TcpServer
    to convey data from multiplexer to ugm_engine."""
    def __init__(self, p_ugm_engine, p_use_tagger):
        """Init server and store ugm engine."""
        self._ugm_engine = p_ugm_engine
        self._use_tagger = p_use_tagger
        if self._use_tagger:
            self._tagger = tagger.get_tagger()

        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.bind((ugm_server.TCP_IP, ugm_server.TCP_PORT))

    def run(self):
        """Do forever:
        wait for data from ugm_server (it should be UgmUpdate() message
        type by now), parse data and send it to self._ugm_engine."""
        try:
            while True:
                # Wait for data from ugm_server
                l_full_data = self.socket.recv(BUF)

                # d should represent UgmUpdate type...
                l_msg = variables_pb2.UgmUpdate()
                try:
                    l_msg.ParseFromString(l_full_data)
                except:
                    LOGGER.info("PARSER ERROR")
                    continue

                l_time = time.time()
                self._ugm_engine.queue_message(l_msg)

                if self._use_tagger:
                    self._tagger.send_tag(l_time, l_time, "ugm_update", 
                                    {"ugm_config":str(l_msg.value)})
        finally:
            self.socket.close()



import configurer
from ugm import ugm_engine
from ugm import ugm_blinking_engine
from ugm import ugm_blinking_connection

if __name__ == "__main__":
    # Create instance of ugm_engine with config manager (created from
    # default config file
    configs = configurer.Configurer(settings.MULTIPLEXER_ADDRESSES).get_configs(['UGM_CONFIG', 'UGM_USE_TAGGER', 'UGM_TYPE'])
    if configs['UGM_TYPE'] == 'SIMPLE':
        ENG = ugm_engine.UgmEngine(ugm_config_manager.UgmConfigManager(configs['UGM_CONFIG']))
    elif configs['UGM_TYPE'] == 'BLINKING':
        connection = ugm_blinking_connection.UgmBlinkingConnection(settings.MULTIPLEXER_ADDRESSES)
        ENG = ugm_engine.UgmBlinkingEngine(ugm_config_manager.UgmConfigManager(configs['UGM_CONFIG']),
                                           connection
                                           )
    else:
        raise Exception("Unrecognised ugm_type: "+str(configs['UGM_TYPE']))

    thread.start_new_thread(UdpServer(ENG, int(configs['UGM_USE_TAGGER'])).run, ())

    # Start multiplexer in a separate process
    path = os.path.join(settings.module_abs_path(), "ugm_server.py")
    os.system("python " + path + " &")


    #TODO - works only when running from openbci directiory...
    # fire ugm engine in MAIN thread (current thread)
    ENG.run()


