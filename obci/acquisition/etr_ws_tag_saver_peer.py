#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from multiplexer.multiplexer_constants import peers
from obci.configs import settings

from obci.acquisition.tag_saver_peer import TagSaver

if __name__ == "__main__":
    TagSaver(settings.MULTIPLEXER_ADDRESSES, peer_type=peers.TOBII_TAG_SAVER).loop()
