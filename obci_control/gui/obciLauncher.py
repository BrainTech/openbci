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

from obci_window import Ui_OBCILauncher

from obci_launcher_engine import OBCILauncherEngine
from experiment_engine_info import MODE_BASIC,MODE_ADVANCED,MODES
import launcher.obci_script as obci_script
from launcher.launcher_tools import NOT_READY, READY_TO_LAUNCH, LAUNCHING, \
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED
from common.message import LauncherMessage

import sys

class ObciLauncherWindow(QMainWindow, Ui_OBCILauncher):
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
        super(ObciLauncherWindow, self).__init__(parent)

        self.server_ip = sys.argv[1] if len(sys.argv) == 2 else None

        client = obci_script.client_server_prep(server_ip=self.server_ip)
        self.engine = OBCILauncherEngine(client, self.server_ip)

        self.setupUi(self)

        if self.server_ip:
            self.setWindowTitle(self.windowTitle() + ' - ' + 'REMOTE CONNECTION TO ' + str(self.server_ip))

        # self.scenarios.horizontalHeader().setResizeMode (QHeaderView.Stretch)

        self.scenarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenarios.setColumnCount(2)
        # self.scenarios.setHorizontalHeaderLabels(["Scenario", "Status"])
        self.scenarios.setHeaderLabels(["Scenario", "Status"])
        # self.scenarios.horizontalHeader().setVisible(True)
        self.scenarios.setColumnWidth(0, 300)
        #self.scenarios.setColumnWidth(1, 100)

        self.scenarios.itemClicked.connect(self._setInfo)
        self.scenarios.currentItemChanged.connect(self._setInfo)

        self.parameters.setHeaderLabels(["Name", 'Value', 'Info'])
        self.parameters.itemClicked.connect(self._itemClicked)
        self.parameters.itemChanged.connect(self._itemChanged)
        self.parameters.setColumnWidth(0, 200)
        self.parameters.setColumnWidth(1, 400)

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

        self.exp_states = {}
        self.exp_widgets = {}

        self.setupMenus()
        self.setupActions()
        self.update_user_interface(None)
        self.show()

    def setupMenus(self):
        self.menuMenu.addAction(self.actionOpen)
        self.menuMenu.addAction(self.actionSave)
        self.menuMenu.addAction(self.actionSave_as)
        self.menuMenu.addAction(self.actionAdd_to_sidebar)
        self.menuMenu.addAction(self.actionRemove_from_sidebar)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionExit)


    def setupActions(self):
        self.actionExit.triggered.connect(PyQt4.QtGui.qApp.quit)

    def setScenarios(self, scenarios):
        scenarios.sort(cmp=lambda a,b: str(a.name) > str(b.name))
        self._scenarios = scenarios
        self.scenarios.setSortingEnabled(True)
        self.scenarios.clear()

        # self.scenarios.setRowCount(len(scenarios))

        self.categories = []
        self.exp_widgets = {}
        for i, s in enumerate(scenarios):
            cat = s.category
            treecat = None
            names = [unicode(c.text(0)) for c in self.categories]
            if cat not in names:
                treecat = ObciTreeWidgetItem([QString(str(cat))], None)

                treecat.setText(0, QString(str(cat)))
                self.categories.append(treecat)
                self.scenarios.addTopLevelItem(treecat)
                treecat.setExpanded(True)
                self.scenarios.expandItem(treecat)
            else:
                treecat = self.categories[names.index(cat)]
            name = ObciTreeWidgetItem([s.name, s.status.status_name], s.uuid)
            self.exp_widgets[s.uuid] = name

            if s.status.status_name:
                name.setBackground(0, QColor(self.status_colors[s.status.status_name]))
                name.setBackground(1, QColor(self.status_colors[s.status.status_name]))
            treecat.addChild(name)
            name.setToolTip(0, QString(s.launch_file))
        self.scenarios.sortItems(0, Qt.AscendingOrder)
        print "SCENARIOS SET"

    def getScenarios(self):
        return self._scenarios

    def _setParams(self, experiment):

        expanded = self.exp_states[experiment.exp.uuid].expanded_peers

        self.parameters.clear()
        self._params = experiment
        experiment = experiment.exp
        for peer_id, peer in experiment.exp_config.peers.iteritems():
            st = experiment.status.peer_status(peer_id).status_name

            parent = QTreeWidgetItem([peer_id, st])
            parent.setFirstColumnSpanned(True)

            parent.setBackground(0, QBrush(QColor(self.status_colors[st])))
            parent.setBackground(1, QBrush(QColor(self.status_colors[st])))
            parent.setBackground(2, QBrush(QColor(self.status_colors[st])))
            parent.setToolTip(0, peer.path)


            self.parameters.addTopLevelItem(parent)

            if parent.text(0) in expanded:
                parent.setExpanded(True)

                parent.setToolTip(0, peer.path)

            params = experiment.parameters(peer_id, self.details_mode.currentText())
            for param, (value, src) in params.iteritems():
                val = unicode(value) #if not src else value + "  ["+src + ']'
                src = src if src else ''
                child = QTreeWidgetItem([param, val, src ])
                if src:
                    child.setDisabled(True)
                parent.addChild(child)

                #child.setToolTip(0, 'Local parameter')
                #child.setToolTip(1, 'Local parameter')

    def _getParams(self):
        if self._params.exp.uuid not in self.exp_states:
            print "stale experiment descriptor"
            return self._params
        state = self.exp_states[self._params.exp.uuid]
        expanded = set()
        for i, peer in enumerate(self._params.exp.exp_config.peers.values()):
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
        peer_id = unicode(item.parent().text(0))
        param = unicode(item.text(0))
        val = unicode(item.text(1))

        old_val = exp.exp_config.param_value(peer_id, param)
        if old_val != unicode(item.text(1)):
            exp.update_peer_param(peer_id, param, val)
            self._getParams()
            self._setParams(self._params)

    def _setInfo(self, scenario_item, column):
        if scenario_item is None:
            print "scenario_item NONE"

        elif scenario_item.uuid not in self.exp_states:
            self._params = None
            self.parameters.clear()
            self.parameters_of.setTitle("Parameters")
        else:
            self.info.setText(self.exp_states[scenario_item.uuid].exp.info)

            if self._params:
                self._getParams()
            self._setParams(self.exp_states[scenario_item.uuid])
            self.parameters_of.setTitle("Parameters of " + self.exp_states[scenario_item.uuid].exp.name)
        self._manage_actions(scenario_item)

    def _start(self):

        self.start.emit(str(self.scenarios.currentItem().uuid))
    def _stop(self):
        self.stop.emit(str(self.scenarios.currentItem().uuid))
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

    def exp_destroyed(self, *args, **kwargs):
        print args
        print kwargs
        print "DESTROYED"

    def update_user_interface(self, update_msg):

        scenarios = self.engine.list_experiments()

        current_sc = self.scenarios.currentItem()
        curr_uid = current_sc.uuid if current_sc is not None else None
        curr_exp_state = self.exp_states.get(curr_uid, None)
        curr_exp = curr_exp_state.exp if curr_exp_state is not None else None
        if curr_exp is not None:
            if curr_exp in scenarios:
                curr_uid = curr_exp.exp_config.uuid
                print "ccccuuurrr uid", curr_uid
        else:
            print "not found", curr_uid, curr_exp

        new_states = {}
        for exp in scenarios:

            if exp.uuid not in self.exp_states:
                st = new_states[exp.uuid] = ExperimentGuiState(exp)
                st.exp.destroyed.connect(self.exp_destroyed)
            else:
                new_states[exp.uuid] = self.exp_states[exp.uuid]

        self.exp_states = new_states

        mode = self.details_mode.currentText()
        if mode not in MODES:
            mode = MODE_ADVANCED
        self.engine.details_mode = mode

        self.setScenarios(scenarios)
        #
        # current_sc = self.scenarios.currentRow()


        if current_sc is None:
            print "current sc None!"
            current_sc = self._first_exp(self.scenarios)
        else:
            current_sc = self.exp_widgets[curr_uid]

        self.scenarios.setCurrentItem(current_sc)
        self._manage_actions(current_sc)

    def _first_exp(self, scenarios):
        exp = None
        print "toplev", scenarios.topLevelItemCount()
        for index in range(scenarios.topLevelItemCount()):
            item = scenarios.topLevelItem(index)
            print "exps: ", item.childCount()
            for ich in range(item.childCount()):
                exp = item.child(ich)
                break
            if exp:
                print "..."
                break
        print "exp", exp
        return exp

    def _manage_actions(self, current_sc):
        if current_sc is None:
            print "_manage_actions current_sc NONE!!!"
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            return
        if current_sc.uuid not in self.exp_states:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            return
        current_exp = self.exp_states[current_sc.uuid].exp

        if current_exp.launcher_data is not None:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.parameters.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            enable = (current_exp.status.status_name == READY_TO_LAUNCH)
            self.start_button.setEnabled(enable)
            self.stop_button.setEnabled(False)
            self.parameters.setEditTriggers(QAbstractItemView.DoubleClicked |\
                                         QAbstractItemView.EditKeyPressed)

        if self.server_ip is not None:
            self.reset_button.setEnabled(False)

        self.actionOpen.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.actionSave_as.setEnabled(False)
        self.actionAdd_to_sidebar.setEnabled(False)
        self.actionRemove_from_sidebar.setEnabled(False)
        self.actionExit.setEnabled(True)

class ObciTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, header_list, experiment_id):
        self.uuid = experiment_id
        super(ObciTreeWidgetItem, self).__init__(header_list)

class ExperimentGuiState(object):
    def __init__(self, engine_experiment):

        self.exp = engine_experiment
        self.expanded_peers = set()


if __name__ == '__main__':
    app = QApplication([])
    dialog = ObciLauncherWindow()

    import sys
    dialog.start.connect(lambda name:sys.stderr.write('Start %s \n' % name))
    dialog.stop.connect(lambda name:sys.stderr.write('Stop %s \n' % name))

    sys.exit(app.exec_())
