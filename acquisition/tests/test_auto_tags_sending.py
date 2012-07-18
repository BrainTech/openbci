#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from utils import tagger
import time

TAGGER = tagger.get_tagger()
COLORS = ['czerwony', 'zielony', 'niebieski', 'bialy']
NAMES = ['pozytywny', 'negatywny', 'neutralny']
import random

from peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types
from obci_configs import settings

class AutoTagGenerator(ConfiguredClient):
    def __init__(self, addresses):
        super(AutoTagGenerator, self).__init__(addresses, peers.TAGS_SENDER)
        self.ready()


    def run(self):
        while True:
            time.sleep(1.0 + random.random()*10.0)
            name = NAMES[random.randint(0, len(NAMES)-1)]

            t= time.time()
            print("SEND TAG name"+name+" with time: "+repr(t))
            if name == 'pozytywny' or name == 'negatywny':
                TAGGER.send_tag(t, t+1.0, name, {'czestosc':random.randint(0, 10),
                                                                  'liczba':random.random(), 
                                                                  'wypelnienie':COLORS[random.randint(0, len(COLORS)-1)], 
                                                                  'tekst': " d jfsld fkjew lkgjew lkgjewlkg jewg ldsj glkds jglkdsg jlkdsg jds"
                                                                     })
            else:
                TAGGER.send_tag(t, t+1.0, name, {'czestosc':random.randint(0, 10),
                                               'wypelnienie':COLORS[random.randint(0, len(COLORS)-1)], 
                                               'poziom': random.randint(100, 1000)})

if __name__ == "__main__":
  AutoTagGenerator(settings.MULTIPLEXER_ADDRESSES).run()

