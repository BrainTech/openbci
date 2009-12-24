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
#

import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

class ManualSpellerLogicControl(object):
    def __init__(self):
        self._connection = connect_client(type = peers.ANALYSIS)
    def run(self):
        l_input = ""
        l_msg_type = types.DECISION_MESSAGE
        print("IF YOU DIDN`T FIRE UGM AND SPELLER LOGIC BEFORE RUNNING THIS SCRIPT DO IT NOW!!!")
        while True:
            print("Type decision message to be sent to logic (a number from 0-7)")
            l_input = raw_input()
            # Decision made, send the decision to logics
            decision = int(l_input)
            dec = variables_pb2.Decision()
            dec.decision = decision
            dec.type = 0
            self._connection.send_message(message = dec.SerializeToString(), type = l_msg_type, flush=True)
if __name__ == "__main__":
    ManualSpellerLogicControl().run()

