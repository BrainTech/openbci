#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import os

from multiplexer.multiplexer_constants import peers, types
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from analysis.obci_signal_processing.signal import data_write_proxy
from obci_configs import settings, variables_pb2
from acquisition import acquisition_logging as logger

LOGGER = logger.get_logger("wii_board_saver", 'info')

DATA_FILE_EXTENSION = '.wii_board.raw'

class WiiBoardSaver(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(WiiBoardSaver, self).__init__(addresses=addresses, 
                                          type=peers.WII_BOARD_SAVER)
        LOGGER.info("Request system settings ...")

        f_dir = os.path.expanduser(os.path.normpath(self.config.get_param("save_file_path")))
        f_name = self.config.get_param("save_file_name")
        if not os.access(f_dir, os.F_OK):
             os.mkdir(f_dir)
        f_path = os.path.normpath(os.path.join(
               f_dir, f_name + DATA_FILE_EXTENSION))
        self._data_proxy = data_write_proxy.get_proxy(f_path)

        self.ready()
        LOGGER.info("WiiSaver init finished!")

    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            self._data_proxy.data_received(l_msg.x)
            self._data_proxy.data_received(l_msg.y)
            self._data_proxy.data_received(l_msg.timestamp)
        self.no_response()

if __name__ == "__main__":
    WiiBoardSaver(settings.MULTIPLEXER_ADDRESSES).loop()
