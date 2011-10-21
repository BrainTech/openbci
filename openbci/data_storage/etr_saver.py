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

import os
from openbci.offline_analysis.obci_signal_processing.signal import data_file_proxy
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2, configurer
import data_storage_logging as logger
LOGGER = logger.get_logger("etr_saver", 'info')


DATA_FILE_EXTENSION = '.etr.dat'
class EtrSaver(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(EtrSaver, self).__init__(addresses=addresses, 
                                          type=peers.ETR_SAVER)
        configurer_ = configurer.Configurer(addresses)
        
        LOGGER.info("Request system settings ...")
        configs = configurer_.get_configs(['SaveFilePath', 'SaveFileName'])
        LOGGER.info("Got system settings ...")

        f_dir = os.path.normpath(configs['SaveFilePath'])
        f_name = configs['SaveFileName']

        if not os.access(f_dir, os.F_OK):
             os.mkdir(f_dir)
        f_path = os.path.normpath(os.path.join(
               f_dir, f_name + DATA_FILE_EXTENSION))

        self._data_proxy = data_file_proxy.DataFileWriteProxy(f_path)

        configurer_.set_configs({'PEER_READY':str(peers.ETR_SAVER)}, self.conn)
        LOGGER.info("EtrSaver init finished!")

    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            self._data_proxy.data_received(l_msg.x)
            self._data_proxy.data_received(l_msg.y)
        self.no_response()

if __name__ == "__main__":
    EtrSaver(settings.MULTIPLEXER_ADDRESSES).loop()
