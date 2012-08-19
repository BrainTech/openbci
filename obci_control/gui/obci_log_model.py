#!/usr/bin/env python
# -*- coding: utf-8 -*-
import thread, time

class LogModel(object):
    def __init__(self):
        self._peers = []
        self._peers_log = {'amplifier': 
                           {'peer_id': 'amplifier', 'logs': []},
                           'mx': 
                           {'peer_id': 'mx', 'logs': []}
                           } #'logs keyed by peer id

        thread.start_new_thread(
                self.run, 
                ()
                )
    def get_peers(self):
        return self._peers

    def get_peer_ind(self, peer_id):
        return self._peers.index(peer_id)

    def add_peer(self, peer_id):
        self._peers.append(peer_id)

    def remove_peer(self, ind):
        self._peers.pop(ind)

    def run(self):
        i = 0
        while True:
            i += 1
            time.sleep(5)
            self._peers_log['amplifier']['logs'].append('Siabada '+str(i))
            #emig self._peers_log['amplifier']
            time.sleep(5)
            self._peers_log['mx']['logs'].append('Siabada '+str(i))
            #emig self._peers_log['x']

