#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import random, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from configs import settings, variables_pb2

class SpellerLogicTest(ConfiguredClient):
    def __init__(self, addresses):
        super(SpellerLogicTest, self).__init__(addresses=addresses, type=peers.ANALYSIS)
        self.times = [float(i) for i in self.config.get_param('times').split(';')]
        self.decs = self.config.get_param('decs').split(';')
        self.count = len(self.decs)
        self.ready()

    def run(self):
        l_input = ""
        l_msg_type = types.DECISION_MESSAGE
        while True:
            ind = random.randint(0, self.count-1)
            decision = self.decs[ind]
            time.sleep(self.times[ind])
            self.conn.send_message(message = decision, type = l_msg_type, flush=True)
if __name__ == "__main__":
    SpellerLogicTest(settings.MULTIPLEXER_ADDRESSES).run()

