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

from PySide.QtGui import *
from PySide.QtCore import *
import PySide.QtGui
from obci_launcher import Ui_ObciLauncher

from obci_launcher_engine import OBCILauncherEngine
import launcher.obci_script as obci_script
from launcher.launcher_tools import NOT_READY, READY_TO_LAUNCH, LAUNCHING, \
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED

class ObciLauncherDialog(QDialog, Ui_ObciLauncher):
    '''
    classdocs
    '''
    start = Signal(str)
    stop = Signal(str)
    reset = Signal(str)
    
    status_colors = {
        NOT_READY : 'dimgrey',
        READY_TO_LAUNCH : 'lightgrey',
        LAUNCHING : 'lightseagreen',
        FAILED_LAUNCH : 'red',
        RUNNING : 'lightgreen',
        FINISHED : 'lightblue',
        FAILED : 'red',
        TERMINATED : 'darkyellow'}


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ObciLauncherDialog, self).__init__(parent)

        client = obci_script.client_server_prep()
        self.engine = OBCILauncherEngine(client)

        self.setupUi(self)
        self.scenarios.horizontalHeader().setResizeMode (QHeaderView.ResizeMode.Stretch)
        self.scenarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenarios.setColumnCount(2)
        self.scenarios.setHorizontalHeaderLabels(["Scenario", "Status"])
        self.scenarios.horizontalHeader().setVisible(True)

        self.scenarios.currentCellChanged.connect(self._setInfo)

        self.parameters.setHeaderLabels(["Name", 'Value'])
        self.parameters.itemClicked.connect(self._itemClicked)
        self.parameters.itemChanged.connect(self._itemChanged)
        self.parameters.setColumnWidth(0, 200)

        # print PySide.QtGui.QColor.colorNames()
        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)
        self.reset_button.clicked.connect(self._reset)

        self._params = []
        self._scenarios = []


        self.engine.update_ui.connect(self.update_user_interface)
        self.reset.connect(self.engine.reset_launcher)
        self.start.connect(self.engine.start_experiment)
        self.stop.connect(self.engine.stop_experiment)

        self.update_user_interface(None)

    def setScenarios(self, scenarios):
        self._scenarios = scenarios
        self.scenarios.clearContents()
        self.scenarios.setRowCount(len(scenarios))
        for i, s in enumerate(scenarios):
            name = QTableWidgetItem(s.name)
            self.scenarios.setItem(i, 0, name)
            # path = QTableWidgetItem(s['path'])
            # self.scenarios.setItem(i, 1, path)            
            status = QTableWidgetItem(s.status.status_name)
            self.scenarios.setItem(i, 1, status)
            
            if s.status.status_name:
                name.setBackground(QColor(self.status_colors[s.status.status_name]))
                status.setBackground(QColor(self.status_colors[s.status.status_name]))

            
            name.setToolTip(s.launch_file)
            status.setToolTip(s.launch_file)
    
    def getScenarios(self):
        # self._scenarios[self.scenarios.currentRow()]['params'] = self._getParams()
        return self._scenarios

    def _setParams(self, experiment):
        expanded = set()
        for i in range(self.parameters.topLevelItemCount()):
            item = self.parameters.topLevelItem(i)
            if item.isExpanded(): expanded.add(item.text(0))
        self.parameters.clear()
        self._params = experiment
        for peer_id, peer in experiment.exp_config.peers.iteritems():
            st = experiment.status.peer_status(peer_id).status_name
            parent = QTreeWidgetItem([peer_id, st])
            # parent.setFirstColumnSpanned(True)
            parent.setBackground(0, PySide.QtGui.QBrush(PySide.QtGui.QColor(self.status_colors[st])))
            parent.setBackground(1, PySide.QtGui.QBrush(PySide.QtGui.QColor(self.status_colors[st])))

            self.parameters.addTopLevelItem(parent)
            if unicode(parent.text(0)) in expanded:
                parent.setExpanded(True)

                parent.setToolTip(0, peer.path)

            for param, value in experiment.exp_config.local_params(peer_id).iteritems():
                child = QTreeWidgetItem([param, str(value)])                
                parent.addChild(child)
                
                child.setToolTip(0, 'Local parameter')
                child.setToolTip(1, child.toolTip(0))

    def _getParams(self):
        for i, peer in enumerate(self._params.exp_config.peers.values()):
            parent = self.parameters.topLevelItem(i)
            for j, param in enumerate(peer.config.local_params.keys()):
                child = parent.child(j)
                # peer.config.update_local_param(param, child.text(1))
                
        return self._params

    def _itemClicked(self, item, column):
        # print "item clicked", item, column
        if item.columnCount() > 1 and column > 0:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        else:
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)


    def _itemChanged(self, item, column):
        if item.parent() is None:
            return
        exp = self._params
        peer_id = item.parent().text(0)
        old_val = exp.exp_config.param_value(peer_id, item.text(0))
        if old_val != item.text(1):
            # exp.exp_config.update_local_param(peer_id, item.text(0), item.text(1))
            exp.update_peer_param(peer_id, item.text(0), item.text(1))
            print "item changed", peer_id, item.text(0), item.text(1), "old val:", old_val


    
    def _setInfo(self, curRow, curCol, lastRow, lastCol):
        print curRow, lastRow
        if curRow == lastRow:
            return
        self.info.setText(self._scenarios[curRow].info)
        if lastRow >= 0:
            self._getParams()
            # self._scenarios[lastRow]['params'] = self._getParams()
            
        self._setParams(self._scenarios[curRow])
        self.parameters_of.setTitle("Parameters of " + self._scenarios[curRow].name)
    
    def _start(self):
        self.start.emit(self._scenarios[self.scenarios.currentRow()].uuid)
    def _stop(self):
        self.stop.emit(self._scenarios[self.scenarios.currentRow()].uuid)
    def _reset(self):
        self.reset.emit(self._scenarios[self.scenarios.currentRow()].uuid)

    def update_user_interface(self, update_msg):
        print "-----updating user interface  / ", update_msg if not update_msg else update_msg.type
        scenarios = self.engine.list_experiments()
        self.setScenarios(scenarios)
        # refresh experiments & params
        # refresh actions
            # editable fields = running / not
            # stop = running
            # start = not_running
        

if __name__ == '__main__':
    app = QApplication([])
    dialog = ObciLauncherDialog()

    import sys
    dialog.start.connect(lambda name:sys.stderr.write('Start %s \n' % name))
    dialog.stop.connect(lambda name:sys.stderr.write('Stop %s \n' % name))
    


    dialog.exec_()
