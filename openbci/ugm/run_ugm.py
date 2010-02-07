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

import socket, thread
import variables_pb2
from ugm import ugm_engine
from ugm import ugm_config_manager
from ugm import ugm_server
import os, sys, subprocess

class TcpServer(object):
    def __init__(self, p_ugm_engine):
        self._ugm_engine = p_ugm_engine
    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((ugm_server.TCP_IP, ugm_server.TCP_PORT))
            s.listen(5)
            while True:
                conn, addr = s.accept()
                d = ''
                while True:
                    data = conn.recv(ugm_server.BUFFER_SIZE)
                    if not data: break
                    d = ''.join([d,data])
                l_msg = variables_pb2.UgmUpdate()
                l_msg.ParseFromString(d)
                self._ugm_engine.update_from_message(
                    int(l_msg.type), l_msg.value)
                conn.close()
        finally:
            s.close()

if __name__ == "__main__":
    e = ugm_engine.UgmEngine(ugm_config_manager.UgmConfigManager())
    thread.start_new_thread(TcpServer(e).run, ())
    os.system("./openbci/ugm/ugm_server.py &")
    #TODO - works only when running from openbci directiory...
    e.run()


