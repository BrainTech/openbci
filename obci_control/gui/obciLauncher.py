#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 13-02-2012

@author: Macias
'''
try:
    from ui_compiler import compile_dir
    compile_dir(__file__)
except:
    pass

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import PyQt4.QtGui
from obci_launcher import Ui_ObciLauncher

from obci_launcher_engine import OBCILauncherEngine, MODE_BASIC,MODE_ADVANCED,MODES
import launcher.obci_script as obci_script
from launcher.launcher_tools import NOT_READY, READY_TO_LAUNCH, LAUNCHING, \
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED
from common.message import LauncherMessage

import sys

class ObciLauncherDialog(QDialog, Ui_ObciLauncher):
    '''
    classdocs
    '''
    start = pyqtSignal(str)
    stop = pyqtSignal(str)
    reset = pyqtSignal(str)
    
    status_colors = {
        NOT_READY : 'dimgrey',
        READY_TO_LAUNCH : 'bisque',
        LAUNCHING : 'lightseagreen',
        FAILED_LAUNCH : 'red',
        RUNNING : 'lightgreen',
        FINISHED : 'lightblue',
        FAILED : 'red',
        TERMINATED : 'khaki'
    }


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ObciLauncherDialog, self).__init__(parent)
        
        self.server_ip = sys.argv[1] if len(sys.argv) == 2 else None

        client = obci_script.client_server_prep(server_ip=self.server_ip)
        self.engine = OBCILauncherEngine(client, self.server_ip)

        self.setupUi(self)

        if self.server_ip:
            self.setWindowTitle(self.windowTitle() + ' - ' + 'REMOTE CONNECTION TO ' + str(self.server_ip))
            
        self.scenarios.horizontalHeader().setResizeMode (QHeaderView.Stretch)

        self.scenarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenarios.setColumnCount(2)
        self.scenarios.setHorizontalHeaderLabels(["Scenario", "Status"])
        self.scenarios.horizontalHeader().setVisible(True)

        self.scenarios.currentCellChanged.connect(self._setInfo)

        self.parameters.setHeaderLabels(["Name", 'Value', 'Info'])
        self.parameters.itemClicked.connect(self._itemClicked)
        self.parameters.itemChanged.connect(self._itemChanged)
        self.parameters.setColumnWidth(0, 200)
        self.parameters.setColumnWidth(1, 200)

        # print PyQt4.QtGui.QColor.colorNames()
        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)
        self.reset_button.clicked.connect(self._reset)

        self._params = []
        self._scenarios = []

        self.details_mode.addItems(MODES)


        self.engine.update_ui.connect(self.update_user_interface)
        self.reset.connect(self.engine.reset_launcher)
        self.start.connect(self.engine.start_experiment)
        self.stop.connect(self.engine.stop_experiment)
        self.details_mode.currentIndexChanged.connect(self.update_user_interface)

        self.exp_states = []
        self.update_user_interface(None)

    def setScenarios(self, scenarios):
        self._scenarios = scenarios
        self.scenarios.clearContents()
        self.scenarios.setRowCount(len(scenarios))
        for i, s in enumerate(scenarios):
            name = QTableWidgetItem(s.name)
            self.scenarios.setItem(i, 0, name)
      
            status = QTableWidgetItem(s.status.status_name)
            self.scenarios.setItem(i, 1, status)
            
            if s.status.status_name:
                name.setBackground(QColor(self.status_colors[s.status.status_name]))
                status.setBackground(QColor(self.status_colors[s.status.status_name]))

            
            name.setToolTip(s.launch_file)
            status.setToolTip(s.launch_file)
    
    def getScenarios(self):
        return self._scenarios

    def _setParams(self, experiment):
        expanded = self.exp_states[self._index_of(experiment)].expanded_peers
        # print "expanded: ", expanded
        # if expanded:
        #     print "exxx", list(expanded)[0].__class__
        self.parameters.clear()
        self._params = experiment
        for peer_id, peer in experiment.exp_config.peers.iteritems():
            st = experiment.status.peer_status(peer_id).status_name

            parent = QTreeWidgetItem([peer_id, st])
            parent.setFirstColumnSpanned(True)

            parent.setBackground(0, PyQt4.QtGui.QBrush(PyQt4.QtGui.QColor(self.status_colors[st])))
            parent.setBackground(1, PyQt4.QtGui.QBrush(PyQt4.QtGui.QColor(self.status_colors[st])))
            parent.setBackground(2, PyQt4.QtGui.QBrush(PyQt4.QtGui.QColor(self.status_colors[st])))
            parent.setToolTip(0, peer.path)


            self.parameters.addTopLevelItem(parent)

            if parent.text(0) in expanded:
                parent.setExpanded(True)

                parent.setToolTip(0, peer.path)

            params = experiment.parameters(peer_id, self.details_mode.currentText())
            for param, (value, src) in params.iteritems():
                val = str(value) #if not src else value + "  ["+src + ']'
                src = src if src else ''
                child = QTreeWidgetItem([param, val, src ])                
                if src:

                    child.setDisabled(True)
                parent.addChild(child)
                
                child.setToolTip(0, 'Local parameter')
                child.setToolTip(1, 'Local parameter')

    def _getParams(self):
        if self._index_of(self._params) is None:
            print "stale experiment descriptor"
            return self._params
        state = self.exp_states[self._index_of(self._params)]
        expanded = set()
        for i, peer in enumerate(self._params.exp_config.peers.values()):
            parent = self.parameters.topLevelItem(i)
            if parent is None:
                print "*****   _getParams:   ", i, peer, "parent none"
                continue
            if parent.isExpanded(): expanded.add(parent.text(0))

            for j, param in enumerate(peer.config.local_params.keys()):
                child = parent.child(j)

        state.expanded_peers = expanded        
        return self._params

    def _itemClicked(self, item, column):

        if item.columnCount() > 1 and column > 0:
            if not item.isDisabled():
                item.setFlags(item.flags() | Qt.ItemIsEditable)
            else:
                item.setFlags(Qt.ItemIsSelectable)
        else:
            if not item.isDisabled():
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            else:
                item.setFlags(Qt.ItemIsSelectable)


    def _itemChanged(self, item, column):
        if item.parent() is None:
            return
        exp = self._params
        peer_id = str(item.parent().text(0))
        param = str(item.text(0))
        val = str(item.text(1))
        
        old_val = exp.exp_config.param_value(peer_id, param)
        if old_val != item.text(1):
            exp.update_peer_param(peer_id, param, val)
            self._getParams()
            self._setParams(self._params)


    def _setInfo(self, curRow, curCol, lastRow, lastCol):

        if curRow == lastRow:
            return
        self.info.setText(self._scenarios[curRow].info)

        if self._params:
            self._getParams()
        self._setParams(self._scenarios[curRow])
        self.parameters_of.setTitle("Parameters of " + self._scenarios[curRow].name)
        self._manage_actions(curRow)
    
    def _start(self):
        self.start.emit(str(self._scenarios[self.scenarios.currentRow()].uuid))
    def _stop(self):
        self.stop.emit(str(self._scenarios[self.scenarios.currentRow()].uuid))
    def _reset(self):
        self.reset.emit(str(self.server_ip))

    def _index_of(self, exp):
        uids = {}
        for i, st in enumerate(self.exp_states):
            uids[st.exp.uuid] = i

        # print "_index_of ",uids, exp.uuid, exp.uuid.__class__
        if exp.uuid in uids:
            return uids[exp.uuid]
        else: return None

    def update_user_interface(self, update_msg):

        scenarios = self.engine.list_experiments()

        current_sc = self.scenarios.currentRow()

        new_states = []
        for i, exp in enumerate(scenarios):
            index = self._index_of(exp)
            if index is None:
                new_states.append(ExperimentGuiState(exp))
            else:
                new_states.append(self.exp_states[index])

        self.exp_states = new_states

        if current_sc == -1:
            current_sc = 0

        mode = self.details_mode.currentText()
        if mode not in MODES:
            mode = MODE_ADVANCED
        self.engine.details_mode = mode

        self.setScenarios(scenarios)
        self.scenarios.setCurrentItem(self.scenarios.item(current_sc, 0))

        self._manage_actions(current_sc)

    def _manage_actions(self, current_sc):
        current_exp = self._scenarios[current_sc]

        if current_exp.launcher_data is not None:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.parameters.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.parameters.setEditTriggers(QAbstractItemView.DoubleClicked |\
                                         QAbstractItemView.EditKeyPressed)

        if self.server_ip is not None:
            self.reset_button.setEnabled(False)
        
class ExperimentGuiState(object):
    def __init__(self, engine_experiment):
        self.exp = engine_experiment
        self.expanded_peers = set()


if __name__ == '__main__':
    app = QApplication([])
    dialog = ObciLauncherDialog()

    import sys
    dialog.start.connect(lambda name:sys.stderr.write('Start %s \n' % name))
    dialog.stop.connect(lambda name:sys.stderr.write('Stop %s \n' % name))
    
    dialog.exec_()
