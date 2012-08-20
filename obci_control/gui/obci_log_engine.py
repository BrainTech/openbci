#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import obci_log_model
from obci_launcher_constants import STATUS_COLORS

class LogEngine(QtCore.QObject):
    def __init__(self, tab_widget):

        QtCore.QObject.__init__(self)
        self.tab_widget = tab_widget
        self.tab_widget.tabCloseRequested.connect(self.tab_closed)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        self.model = obci_log_model.LogModel()
        self._prev_model = self.model
        self._init_tab_shortcut()

    def show(self, experiment):
        if self._prev_model != experiment.log_model:
            self._prev_model = self.model
            self.model = experiment.log_model
            self.exp = experiment.exp
            self._prev_model.set_running(False)
            self._rebuild_tab_widget()
            self.model.set_running(True)

    def tab_closed(self, tab_id):
        if tab_id > 0:
            self.model.remove_peer(tab_id-1)
            self.tab_widget.removeTab(tab_id)

    def tab_changed(self, tab_id):
        if tab_id > 0:
            pass
            #self._request_update_log()

    def update_user_interface(self):
        self._update_tab_status()

    def update_log(self, log):
        try:
            ind = self.model.get_peer_ind(log[QtCore.QString('peer_id')])
            #if self.tab_widget.currentIndex()-1 == ind:
            w = self.tab_widget.widget(ind+1)
            w.append('\n'.join([str(l) for l in log[QtCore.QString('logs')]]))
                #t.verticalScrollBar().setSliderPosition(t.verticalScrollBar().maximum())
        except ValueError:
            pass

    def show_log(self, peer_id, scenario_id):

        #TODO - create model.socket if needed
        try:
            ind = self.model.get_peer_ind(peer_id) + 1
            self._show_tab(ind)
        except ValueError: #this tab is not opened yet
            self.model.add_peer(peer_id)
            self.tab_widget.addTab(self._get_log_widget(), peer_id)
            self._update_tab_status()
            self._show_tab(len(self.model.get_peers()))

    def experiment_stopped(self):
        print 'stop'
        #TODO - stop model. socket

    def _rebuild_tab_widget(self):
        scenario = self.tab_widget.widget(0)
        self.tab_widget.clear()
        self.tab_widget.addTab(scenario, "Scenario")
        for t in self.model.get_peers():
            self.tab_widget.addTab(self._get_log_widget(), t)
        print "REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEBILD"
        self._request_update_log()
        self._update_tab_status()

    def _init_tab_shortcut(self):
        self.m = QtCore.QSignalMapper(self)
        self.shortcuts = []
        for i in range(9):
            s = QtGui.QShortcut(QtGui.QKeySequence("Alt+"+str(i+1)), self.tab_widget)
            s.connect(s, QtCore.SIGNAL('activated()'), self.m, QtCore.SLOT('map()'))
            self.m.setMapping(s, i)
            self.shortcuts.append(s)
            self.connect(self.m, QtCore.SIGNAL('mapped(int)'), self, QtCore.SLOT('_show_tab(int)'))

    def _update_tab_status(self):
        for i, peer_id in enumerate(self.model.get_peers()):
            st = self.exp.status.peer_status(str(peer_id)).status_name
            c = STATUS_COLORS[st]
            p = QtGui.QPixmap(16,16)
            p.fill(QtGui.QColor(c))
            ic = QtGui.QIcon()
            ic.addPixmap(p)
            self.tab_widget.setTabIcon(i+1, ic)

    @QtCore.pyqtSlot('int')
    def _show_tab(self, tab_id):
        self.tab_widget.setCurrentIndex(tab_id)

    def _request_update_log(self):
        self.model.emit_logs()

    def _get_log_widget(self):
        w = QtGui.QTextEdit(self.tab_widget)
        w.setReadOnly(True)
        return w



        
