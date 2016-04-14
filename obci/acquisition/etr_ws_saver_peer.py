#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from multiplexer.multiplexer_constants import peers
from obci.configs import settings

from obci.acquisition.signal_saver_peer import SignalSaver

if __name__ == "__main__":
    SignalSaver(settings.MULTIPLEXER_ADDRESSES, peer_type=peers.TOBII_SIGNAL_SAVER).loop()
