#!/usr/bin/env python
# -*- coding: utf-8 -*-
import obci_log_model
import time

class DummyLogModel(obci_log_model.LogModel):
    def __init__(self):
        super(DummyLogModel, self).__init__()
        self._ind = 0
        self._peers_log = {'amplifier': 
                           {'peer_id': 'amplifier', 'logs': []},
                           'mx': 
                           {'peer_id': 'mx', 'logs': []}
                           } #'logs keyed by peer id


    def next_log(self):
        time.sleep(0.05)
        self._ind += 1
        if self._ind % 2 == 0:
            return 'amplifier', 'AMP '+str(self._ind)
        else:
            return 'mx', 'MX '+str(self._ind)

    def post_run(self):
        pass
