#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os
#import speller_graphics_manager as sgm

from multiplexer.multiplexer_constants import peers, types

from obci_configs import settings, variables_pb2
from logic import logic_speller_peer

class LogicHome(logic_speller_peer.LogicSpeller):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        self._states = [0]*8
        super(LogicHome, self).__init__(addresses=addresses)

    def solve(self, i):
        return self._states[i]

    def _run_pre_actions(self, dec):
        self._states[dec] = (self._states[dec] + 1) % 2
        super(LogicHome, self)._run_pre_actions(dec)


    # --------------------------------------------------------------------------
    # ------------------ actions available in config ---------------------------

if __name__ == "__main__":
    LogicHome(settings.MULTIPLEXER_ADDRESSES).loop()

