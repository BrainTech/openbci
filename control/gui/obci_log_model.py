#!/usr/bin/env python
# -*- coding: utf-8 -*-
import thread, time
from PyQt4 import QtCore

class LogModel(QtCore.QObject):
    update_log = QtCore.pyqtSignal(dict)
    def __init__(self):
        super(LogModel, self).__init__()
        self._peers = []
        self._emmit = False
        self._run = False
        self._is_running = False
        self._mutex = QtCore.QMutex()
        self._peers_log = {}

    def connect_running(self, exp):
        self._start_thread(exp)

    def start_running(self, exp):
        self._start_thread(exp)

    def _start_thread(self, exp):
        #self._exp = exp
        self._run = True
        self._is_running = True
        thread.start_new_thread(
                self.run, 
                ()
                )

    def stop_running(self):
        self._run = False

    def is_running(self):
        return self._is_running

    def get_peers(self):
        return self._peers

    def get_peer_ind(self, peer_id):
        return self._peers.index(peer_id)

    def add_peer(self, peer_id):
        self._peers.append(peer_id)

    def remove_peer(self, ind):
        self._peers.pop(ind)

    def set_emmiting(self, flag):
        self._emmit = flag

    def emit_logs(self):
        self._mutex.lock()
        for peer_id, log in self._peers_log.iteritems():
            self.update_log.emit(log)
        self._mutex.unlock()

    def run(self):
        print("model start running ")
        while self._run:
            peer_id, log = self.next_log()
            if peer_id is None:
                #print ("obci_log_model - ERROR IN RECEIVING LOG ON SOCKET OR TIMEOUT!")
                time.sleep(0.1)
            else:
                self._mutex.lock()
                if not self._peers_log.has_key(peer_id):
                    self._peers_log[peer_id] = {'peer_id':peer_id,
                                                'logs':[]}
                self._peers_log[peer_id]['logs'].append(log)
                if self._emmit:
                    e = {'peer_id':peer_id, 'logs':[log]}
                    self.update_log.emit(e)
                self._mutex.unlock()

        print ("obci log model - model stoped running ")
        self.post_run()
        self._is_running = False

