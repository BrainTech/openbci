#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from multiplexer.multiplexer_constants import peers
from obci.configs import settings
from sample_2d_router import Sample2DRouter

if __name__ == "__main__":
    Sample2DRouter(settings.MULTIPLEXER_ADDRESSES, peers.WII_BOARD_SIGNAL_CATCHER).run()
