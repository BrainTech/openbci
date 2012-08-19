#!/usr/bin/env python
# -*- coding: utf-8 -*-
import thread, time
from PyQt4 import QtCore

class LogModel(QtCore.QObject):
    update_log = QtCore.pyqtSignal(dict)
    def __init__(self):
        super(LogModel, self).__init__()
        self._peers = []
        self._running = False
        self._mutex = QtCore.QMutex()
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

    def set_running(self, flag):
        self._running = flag

    def get_logs(self):
        return self._peers_log

    def emit_logs(self):
        self._mutex.lock()
        for peer_id, log in self._peers_log.iteritems():
            self.update_log.emit(log)
        self._mutex.unlock()
        #TODO mutex

    def run(self):
        i = 0
        while True:
            #TODO MUTEX
            if self._running:
                i += 1
                self._mutex.lock()
                time.sleep(0.05)
                self._peers_log['amplifier']['logs'].append('AMP '+str(i))
                e = {'peer_id':'amplifier', 'logs':['AMP '+str(i)]}
                self.update_log.emit(e)
            #emig self._peers_log['amplifier']
                time.sleep(0.05)
                self._peers_log['mx']['logs'].append('MX '+str(i))
                e = {'peer_id':'mx', 'logs':['MX '+str(i)]}
                self.update_log.emit(e)
                self._mutex.unlock()
            #emig self._peers_log['x']
            else:
                time.sleep(0.1)

