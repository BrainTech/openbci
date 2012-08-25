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
        self._model = obci_log_model.LogModel()
        self._prev_model = self._model
        self._init_tab_shortcut()

    def show(self, experiment):
        """Called from gui when scenario`s moules panel is being refreshed,
        eg. when user clicks some new scenario or gui is autmatically being refreshed"""
        if self._prev_model != experiment.log_model:
            self._prev_model = self._model
            self._model = experiment.log_model
            self._exp = experiment.exp
            self._prev_model.set_emmiting(False)
            self._rebuild_tab_widget()
            self._model.set_emmiting(True)
            if self._exp.status.status_name in ['launching', 'running'] and \
                    not self._model.is_running():
                self._model.start_running()

    def tab_closed(self, tab_id):
        """Called on tab_closed event from GUI"""
        if tab_id > 0:
            self._model.remove_peer(tab_id-1)
            self.tab_widget.removeTab(tab_id)

    def tab_changed(self, tab_id):
        """Called on tab_changed event from GUI"""
        if tab_id > 0:
            t = self.tab_widget.widget(tab_id)
            t.verticalScrollBar().setSliderPosition(t.verticalScrollBar().maximum())

    def update_user_interface(self):
        """Called from gui on refresh_gui request.
        Update tabs status in case module`s status
        has changed."""
        self._update_tab_status()

    def update_log(self, log):
        try:
            ind = self._model.get_peer_ind(log[QtCore.QString('peer_id')])
            w = self.tab_widget.widget(ind+1)
            w.append('\n'.join([str(l) for l in log[QtCore.QString('logs')]]))
        except ValueError:
            pass

    def show_log(self, peer_id, scenario_id):
        """Called from gui when user requests peer_id module`s
        log. Lets create and show it..."""
        
        #TODO - create model.socket if needed
        try:
            ind = self._model.get_peer_ind(peer_id) + 1
            self._show_tab(ind)
        except ValueError: #this tab is not opened yet
            self._model.add_peer(peer_id)
            self.tab_widget.addTab(self._get_log_widget(), peer_id)
            self._update_tab_status()
            self._show_tab(len(self._model.get_peers()))

    def experiment_stopped(self):
        print 'experiment stopped'
        self._model.stop_running()

    def experiment_started(self):
        print 'experiment started'
        self._model.start_running()

    def _rebuild_tab_widget(self):
        scenario = self.tab_widget.widget(0)
        self.tab_widget.clear()
        self.tab_widget.addTab(scenario, "Scenario")
        for t in self._model.get_peers():
            self.tab_widget.addTab(self._get_log_widget(), t)
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
        for i, peer_id in enumerate(self._model.get_peers()):
            st = self._exp.status.peer_status(str(peer_id)).status_name
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
        self._model.emit_logs()

    def _get_log_widget(self):
        w = QtGui.QTextEdit(self.tab_widget)
        w.setReadOnly(True)
        return w



        
