#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import logic_multiple_speller_engine
import logic_multiple_speller_server
import settings

import sys, os.path
import settings
if __name__ == "__main__":
    l_server = logic_multiple_speller_server.LogicMultipleSpellerServer(settings.MULTIPLEXER_ADDRESSES)
    l_engine = logic_multiple_speller_engine.LogicMultipleSpellerEngine(l_server)
    l_server.set_engine(l_engine)
    l_server.loop()

 
