#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from multiplexer.multiplexer_constants import peers
from obci.configs import settings

from obci.acquisition.info_saver_peer import InfoSaver

if __name__ == "__main__":
    InfoSaver(settings.MULTIPLEXER_ADDRESSES, peer_type=peers.TOBII_INFO_SAVER).loop()
