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

import socket
import codecs
import json
import sys
import os
import os.path
import sip
import time
import getopt

from obci_window import Ui_OBCILauncher
from connect_dialog import Ui_ConnectToMachine
from obci.utils.filesystem import checkpidfile, removepidfile
from obci.utils.openbci_logging import get_logger, log_crash

from obci_launcher_engine import OBCILauncherEngine, USER_CATEGORY
from obci_launcher_constants import STATUS_COLORS
from experiment_engine_info import MODE_BASIC,MODE_ADVANCED,MODES
import obci.control.launcher.obci_script as obci_script
from obci.control.launcher.launcher_tools import NOT_READY, READY_TO_LAUNCH, LAUNCHING, \
                FAILED_LAUNCH, RUNNING, FINISHED, FAILED, TERMINATED

import obci.control.common.obci_control_settings as settings
from obci.control.common.message import LauncherMessage
import obci.control.common.net_tools as net

import obci_log_engine
#import obci_log_model_dummy
import obci_log_model_real

class ObciLauncherWindow(QMainWindow, Ui_OBCILauncher):
    '''
    classdocs
    '''
    start = pyqtSignal(str, object)
    stop = pyqtSignal(str, bool)
    reset = pyqtSignal(str)

    save_as = pyqtSignal(object)
    remove_user_preset = pyqtSignal(object)
    import_scenario = pyqtSignal(str)

    engine_reinit = pyqtSignal(object)

    @log_crash
    def __init__(self):
        '''
        Constructor
        '''
        QMainWindow.__init__(self)

        self.logger = get_logger('launcherGUI', obci_peer=self)

        self.setupUi(self)
        self.basic_title = self.windowTitle()

        self.exp_states = {}
        self.exp_widgets = {}

        self.scenarioTab.setTabText(0, "Scenario")
        self.scenarioTab.setTabsClosable(True)
        self.log_engine = obci_log_engine.LogEngine(self.scenarioTab)

        self.engine_server_setup()

        self._nearby_machines = self.engine.nearby_machines()

        self.scenarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenarios.setColumnCount(2)
        self.scenarios.setHeaderLabels(["Scenario", "Status"])
        self.scenarios.setColumnWidth(0, 300)

        self.scenarios.itemClicked.connect(self._setInfo)
        self.scenarios.currentItemChanged.connect(self._setInfo)

        self.details_mode.currentIndexChanged.connect(self.update_user_interface)

        self.parameters.setHeaderLabels(["Name", 'Value', 'Info'])
        self.parameters.itemClicked.connect(self._itemClicked)
        self.parameters.itemChanged.connect(self._itemChanged)
        self.parameters.itemDoubleClicked.connect(self._itemDoubleClicked)
        self.parameters.setColumnWidth(0, 200)
        self.parameters.setColumnWidth(1, 400)

        self.machines_dialog = ConnectToMachine(self)

        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)
        #self.reset_button.clicked.connect(self._reset)
        self.store_container.hide()
        self.store_checkBox.stateChanged.connect(self._update_store)
        self.store_dir_chooser.clicked.connect(self._choose_dir)

        self._params = []
        self._scenarios = []

        self.details_mode.addItems(MODES)

        self.engine_reinit.connect(self.engine_server_setup)

        self.setupMenus()
        self.setupActions()
        self.update_user_interface(None)
        self.showMaximized()
        if os.environ.get('OBCI_INSTALL_DIR') != None:
            PyQt4.QtGui.QMessageBox.information(self, "Non standard OpenBCI directory",
                                                "OpenBCI is launched from local directory: "+os.environ.get('OBCI_INSTALL_DIR')+', to start default package version launch "obci_local_remove" in terminal.')


    @log_crash
    def closeEvent(self, e):
        progress = QProgressDialog(self,Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        progress.setLabelText("Finishing...")
        progress.setRange(0,5)
        progress.setCancelButton(None)
        progress.show()
        self.stop_logs()
        removepidfile('gui.pid')
        
        for i in range(5):
            time.sleep(0.4)
            progress.setValue(i+1)
        e.accept()

    def _crash_extra_tags(self, exception=None):
        return {'obci_part' : 'launcher'}

    def stop_logs(self):
        for i, st in self.exp_states.iteritems():
            st.log_model.stop_running()

    @log_crash
    def engine_server_setup(self, server_ip_host=None):
        server_ip, server_name = server_ip_host or (None, None)
        old_ip = None
        old_hostname = None
        if hasattr(self, 'server_ip'):
            old_ip = self.server_ip
            old_hostname = self.server_hostname

        self.server_ip = str(server_ip)
        self.server_hostname = str(server_name)
        ctx = None
        if server_ip is None:
            self.server_ip = '127.0.0.1'
            self.server_hostname = socket.gethostname()

        if hasattr(self, 'engine'):
            client = self.engine.client
            ctx = client.ctx
        else:
            self.engine = None

        if old_ip != self.server_ip and old_hostname != self.server_hostname:

            if self.engine is not None:
                self.engine.cleanup()
                self._disconnect_signals()

                # self.engine.deleteLater()
                sip.delete(self.engine)
                del self.engine
                self.engine = None


            client = obci_script.client_server_prep(server_ip=self.server_ip,
                                                    zmq_ctx=ctx,
                                                    start_srv=True)
            if client is None:
                self.quit()
            self.exp_states = {}
            self.engine = OBCILauncherEngine(client, self.server_ip)
            self._connect_signals()

        if self.server_ip and self.server_hostname != socket.gethostname():
            self.setWindowTitle(self.basic_title + ' - ' + 'remote connection ' + \
                                ' (' +self.server_ip + ' - ' + self.server_hostname + ')')
        else:
            self.setWindowTitle(self.basic_title + ' - ' + 'local connection (' +\
                                                self.server_hostname + ')')

        if old_ip is not None:
            self.engine.update_ui.emit(None)

    def _connect_signals(self):
        self.engine.update_ui.connect(self.update_user_interface)
        self.engine.update_ui.connect(self.log_engine.update_user_interface)
        self.engine.rq_error.connect(self.launcher_error)
        self.engine.saver_msg.connect(self._saver_msg)
        self.reset.connect(self.engine.reset_launcher)
        self.start.connect(self.engine.start_experiment)
        self.start.connect(self.log_engine.experiment_started)
        self.stop.connect(self.engine.stop_experiment)
        self.stop.connect(self.log_engine.experiment_stopped)
        self.save_as.connect(self.engine.save_scenario_as)
        self.import_scenario.connect(self.engine.import_scenario)
        self.remove_user_preset.connect(self.engine.remove_preset)

    def _disconnect_signals(self):
        self.engine.update_ui.disconnect()
        self.engine.rq_error.disconnect()
        self.engine.obci_state_change.disconnect()
        self.engine.saver_msg.disconnect()
        self.reset.disconnect()
        self.start.disconnect()
        self.stop.disconnect()
        self.save_as.disconnect()
        self.import_scenario.disconnect()
        self.remove_user_preset.disconnect()

    def setupMenus(self):
        self.menuMenu.addAction(self.actionOpen)
        self.menuMenu.addAction(self.actionSave_as)
        self.menuMenu.addAction(self.actionRemove_from_sidebar)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionConnect)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionExit)


    def setupActions(self):
        self.actionExit.triggered.connect(PyQt4.QtGui.qApp.quit)
        self.actionConnect.triggered.connect(self._connect_to_machine)
        self.actionSave_as.triggered.connect(self._save_current_as)
        self.actionOpen.triggered.connect(self._import)
        self.actionRemove_from_sidebar.triggered.connect(self._remove_from_sidebar)

    @log_crash
    def setScenarios(self, scenarios):
        scenarios.sort(cmp=lambda a,b: str(a.name) > str(b.name))
        self._scenarios = scenarios
        self.scenarios.setSortingEnabled(True)
        self.scenarios.clear()

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
                treecat.setExpanded(False)
            else:
                treecat = self.categories[names.index(cat)]
            name = ObciTreeWidgetItem([s.name, s.status.status_name], s.uuid)
            self.exp_widgets[s.uuid] = name

            if s.status.status_name:
                name.setBackground(0, QColor(STATUS_COLORS[s.status.status_name]))
                name.setBackground(1, QColor(STATUS_COLORS[s.status.status_name]))
            treecat.addChild(name)
            name.setToolTip(0, QString(s.launch_file))
        self.scenarios.sortItems(0, Qt.AscendingOrder)

    def getScenarios(self):
        return self._scenarios

    @log_crash
    def _setParams(self, experiment):
        expanded = self.exp_states[experiment.exp.uuid].expanded_peers

        self.parameters.clear()
        self._params = experiment
        experiment = experiment.exp
        for peer_id, peer in experiment.exp_config.peers.iteritems():
            st = experiment.status.peer_status(peer_id).status_name
            mch = str(peer.machine) or str(experiment.origin_machine)
            print mch, peer_id
            parent = QTreeWidgetItem([peer_id, st, mch])
            parent.setFirstColumnSpanned(True)

            parent.setBackground(0, QBrush(QColor(STATUS_COLORS[st])))
            parent.setBackground(1, QBrush(QColor(STATUS_COLORS[st])))
            parent.setBackground(2, QBrush(QColor(STATUS_COLORS[st])))
            parent.setToolTip(0, unicode(peer.path))

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

    @log_crash
    def _getParams(self):
        uid = self._params.exp.exp_config.uuid
        old_uid = self._params.exp.old_uid
        if uid not in self.exp_states and old_uid not in self.exp_states:
            print "stale experiment descriptor"
            return self._params
        state = self.exp_states.get(uid, self.exp_states.get(old_uid, None))
        if state is None:
            print "_getParams - experiment not found"
            return self._params
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

    def _itemDoubleClicked(self, item, column):
        if item.parent() is None and column != 2:
            uid = str(self.scenarios.currentItem().uuid)
            #self.exp_states[uid].exp.exp_config.peers[
            self.log_engine.show_log(item.text(0), uid)

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
        changed = False
        if item.parent() is None:
            if column == 2:
                machine = unicode(item.text(2))
                peer_id = unicode(item.text(0))
                old_ma = self._params.exp.exp_config.peer_machine(peer_id)
                if old_ma != machine:
                    self._params.exp.exp_config.update_peer_machine(peer_id, machine)
                    changed = True
        else:
            exp_state = self._params
            peer_id = unicode(item.parent().text(0))
            param = unicode(item.text(0))
            val = unicode(item.text(1))

            old_val = exp_state.exp.exp_config.param_value(peer_id, param)
            if old_val != unicode(item.text(1)):
                exp_state.exp.update_peer_param(peer_id, param, val)
                changed = True

        if changed:
            self._getParams()
            self._setParams(self._params)

    @log_crash
    def _setInfo(self, scenario_item, column):
        if scenario_item is None:
            pass
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
            self._store_update_info(self.exp_states[scenario_item.uuid].store_options)
            self.log_engine.show(self.exp_states[scenario_item.uuid])

        self._manage_actions(scenario_item)

    # @log_crash
    def _start(self):
        uid = str(self.scenarios.currentItem().uuid)
        if self.store_checkBox.isChecked():
            store_options = {u'save_file_name': unicode(self.store_file.text().toUtf8(), 'utf-8'),
                             u'save_file_path': unicode(self.store_dir.text().toUtf8(), 'utf-8'),
                             u'append_timestamp':  unicode(1 if self.store_ts_checkBox.isChecked() else 0),
                             u'store_locally': 1 if self.store_local_checkBox.isChecked() else 0
                             }
            self.exp_states[uid].store_options = store_options
        else:
            store_options = None
        self.log_engine.on_experiment_start(self.exp_states[uid].exp)
        print "obciLauncher - _start(), exp:  ", self.exp_states[uid].exp
        self.start.emit(uid, store_options)

    def _stop(self):
        uid = str(self.scenarios.currentItem().uuid)
        self.exp_states[uid].log_model.stop_running()
        self.stop.emit(uid, self.exp_states[uid].store_options is not None)
        self.exp_states[uid].store_options = None

    @log_crash
    def _saver_msg(self, killer_proc):
        print "GUI SAVER MSG"
        reply = QMessageBox.question(self, 'Signal saving',
            "Signal saving is taking quite some time. This is normal for longer EEG sessions.\n"
            "Continue saving?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)
        killer_proc.poll()
        if reply == QMessageBox.No and killer_proc.returncode is None:
            print "KILLING"
            killer_proc.kill()
            killer_proc.wait()
            print killer_proc.returncode, "^^^"


    def _update_store(self, state):
        if int(state):
            self.store_container.show()
        else:
            self.store_container.hide()


    def _reset(self):
        self.reset.emit(str(self.server_ip))

    def _connect_to_machine(self):
        self.machines_dialog.set_nearby_machines(self._nearby_machines,
                                    self.server_hostname, self.server_ip)
        if self.machines_dialog.exec_():
            self.stop_logs()
            new_ip, new_name = self.machines_dialog.chosen_machine
            self.engine_reinit.emit((new_ip, new_name))
            self.update_user_interface(None)

    def _save_current_as(self):
        filename = QFileDialog.getSaveFileName(self, "Save scenario as..,",
                            os.path.join(settings.DEFAULT_SCENARIO_DIR),
                            'INI files (*.ini)')
        if not filename:
            return
        filename = str(filename)
        if not filename.endswith('.ini'):
            filename += '.ini'

        uid = self.scenarios.currentItem().uuid
        exp = self.exp_states[uid].exp
        self.save_as.emit((filename, exp))

    def _choose_dir(self):
        curr = str(self.store_dir.text())
        if len(curr) == 0:
            curr = '~'
        curr = os.path.expanduser(curr)
        if self.server_hostname != socket.gethostname():
            PyQt4.QtGui.QMessageBox.information(self, "This is a remote connection",
                                                "Enter the directory path by hand.")
            direc = curr
        else:
            direc = QFileDialog.getExistingDirectory(self, "Choose directory..,", curr)

        if not direc:
            return

        self.store_dir.setText(direc)

    def _import(self):
        filename = QFileDialog.getOpenFileName(self, "Import scenario...",
                            os.path.join(settings.DEFAULT_SCENARIO_DIR),
                            'INI files (*.ini)')
        if not filename:
            return
        self.import_scenario.emit(filename)

    def _remove_from_sidebar(self):
        uid = self.scenarios.currentItem().uuid
        exp = self.exp_states[uid].exp
        self.remove_user_preset.emit(exp)

    def exp_destroyed(self, *args, **kwargs):
        print args, kwargs
        print "DESTROYED"

    def launcher_error(self, error_msg):
        if isinstance(error_msg.details, dict):
            str_details = str(json.dumps(error_msg.details, sort_keys=True, indent=4))
        else:
            str_details = str(error_msg.details)
        QMessageBox.critical(self, "Request error", "Error: " +str(error_msg.err_code) +\
                                    "\nDetails: " + str_details,
                                    QMessageBox.Ok)

    @log_crash
    def update_user_interface(self, update_msg):
        user_imported_uuid = None
        if isinstance(update_msg, LauncherMessage):
            if update_msg.type == 'nearby_machines':
                self._nearby_machines = self.engine.nearby_machines()
            elif update_msg.type == '_user_set_scenario':
                user_imported_uuid = update_msg.uuid

        scenarios = self.engine.list_experiments()

        current_sc = self.scenarios.currentItem()
        curr_uid = current_sc.uuid if current_sc is not None else None
        curr_exp_state = self.exp_states.get(curr_uid, None)
        curr_exp = curr_exp_state.exp if curr_exp_state is not None else None
        if curr_exp is not None:
            if curr_exp in scenarios:
                curr_uid = curr_exp.exp_config.uuid
        else:
            print "not found", curr_uid, curr_exp
            current_sc = None

        new_states = {}
        for exp in scenarios:
            if exp.uuid not in self.exp_states:
                st = new_states[exp.uuid] = ExperimentGuiState(
                    self.engine.client,
                    exp,
                    self.log_engine,
                    self.exp_states.get(exp.old_uid, None)
                    )
                st.exp.destroyed.connect(self.exp_destroyed)
            else:
                new_states[exp.uuid] = self.exp_states[exp.uuid]

        self.exp_states = new_states

        mode = self.details_mode.currentText()
        if mode not in MODES:
            mode = MODE_ADVANCED
        self.engine.details_mode = mode

        self.setScenarios(scenarios)

        if user_imported_uuid is not None:
            current_sc = self.exp_widgets.get(user_imported_uuid,
                            self._first_exp(self.scenarios))
        elif current_sc is None:
            current_sc = self._first_exp(self.scenarios)
        else:
            uid = curr_exp.exp_config.uuid
            old_uid = curr_exp.old_uid
            current_sc = self.exp_widgets.get(uid,
                            self.exp_widgets.get(old_uid, self._first_exp(self.scenarios)))

        self.scenarios.setCurrentItem(current_sc)
        self._manage_actions(current_sc)

    def _first_exp(self, scenarios):
        exp = None
        for index in range(scenarios.topLevelItemCount()):
            item = scenarios.topLevelItem(index)
            for ich in range(item.childCount()):
                exp = item.child(ich)
                break
            if exp:
                break
        return exp

    def _manage_actions(self, current_sc):
        if current_sc is None:
            self.start_button.setEnabled(False)
            self._store_set_enabled(False)
            self.stop_button.setEnabled(False)
            return
        if current_sc.uuid not in self.exp_states:
            self.start_button.setEnabled(False)
            self._store_set_enabled(False)
            self.stop_button.setEnabled(False)
            return
        current_exp = self.exp_states[current_sc.uuid].exp

        if current_exp.launcher_data is not None:
            self.start_button.setEnabled(False)
            self._store_set_enabled(False)
            self.stop_button.setEnabled(True)
            self.parameters.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            enable = (current_exp.status.status_name == READY_TO_LAUNCH)
            self.start_button.setEnabled(enable)
            self._store_set_enabled(enable and "amplifier" in current_exp.exp_config.peers)
            self.stop_button.setEnabled(False)
            self.parameters.setEditTriggers(QAbstractItemView.DoubleClicked |\
                                         QAbstractItemView.EditKeyPressed)


        launched = current_exp.status.status_name not in [LAUNCHING, RUNNING, FAILED, TERMINATED]
        self.actionOpen.setEnabled(True)
        self.actionSave_as.setEnabled(launched)
        if current_exp.preset_data is not None:
            remove_enabled = current_exp.preset_data["category"] == USER_CATEGORY
            self.actionRemove_from_sidebar.setEnabled(remove_enabled)
        self.actionExit.setEnabled(True)

        self.actionConnect.setEnabled(self._nearby_machines != {})

    def _store_set_enabled(self, enable):
        self.store_checkBox.setEnabled(enable)
        self.store_file.setEnabled(enable)
        self.store_dir.setEnabled(enable)
        self.store_dir_chooser.setEnabled(enable)
        self.store_ts_checkBox.setEnabled(enable)
        # self.store_local_checkBox.setEnabled(enable)

    def _store_update_info(self, store_options):
        if store_options is not None:
            self.store_file.setText(store_options[u'save_file_name'])
            self.store_dir.setText(store_options[u'save_file_path'])
            self.store_ts_checkBox.setChecked(int(store_options[u'append_timestamp']))
            # self.store_local_checkBox.setChecked(store_options[u'store_locally'])
            self.store_checkBox.setChecked(True)
            self.store_container.show()
        else:
            self.store_checkBox.setChecked(False)
            self.store_container.hide()


class ObciTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, header_list, experiment_id):
        self.uuid = experiment_id
        super(ObciTreeWidgetItem, self).__init__(header_list)

class ExperimentGuiState(object):
    def __init__(self, srv_client, engine_experiment, log_engine, old_exp=None):

        self.exp = engine_experiment
        self.expanded_peers = set()
        if old_exp is None:
            self.store_options = None
            self.log_model = obci_log_model_real.RealLogModel(srv_client)
            self.log_model.update_log.connect(log_engine.update_log)
        else:
            self.store_options = old_exp.store_options
            self.log_model = old_exp.log_model


class ConnectToMachine(QDialog, Ui_ConnectToMachine):
    def __init__(self, parent):
        super(ConnectToMachine, self).__init__(parent)
        self.setupUi(self)
        self.nearby_machines.horizontalHeader().setResizeMode (QHeaderView.Stretch)

        self.nearby_machines.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.nearby_machines.setColumnCount(3)
        self.nearby_machines.setHorizontalHeaderLabels(["IP", "Hostname", "Status"])
        self.nearby_machines.horizontalHeader().setVisible(True)
        self.nearby_machines.setColumnWidth(0, 200)
        self.nearby_machines.itemDoubleClicked.connect(self.accept)

        self.chosen_machine = None


    def set_nearby_machines(self, machines, current_hostname, current_ip):
        self.nearby_machines.clearContents()
        self.nearby_machines.setRowCount(len(machines))
        for i, (ip, hostname) in enumerate(list(machines.iteritems())):
            ip_w = QTableWidgetItem(ip)
            ip_w.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.nearby_machines.setItem(i, 0, ip_w)

            hn_w = QTableWidgetItem(hostname)
            hn_w.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.nearby_machines.setItem(i, 1, hn_w)

            st_w = QTableWidgetItem()
            st_w.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if (str(ip) == str(current_ip) or str(current_ip) == net.lo_ip())\
                                 and str(hostname) == str(current_hostname):
                font = QFont()
                font.setWeight(QFont.Black)
                hn_w.setFont(font)
                ip_w.setFont(font)
                st_w.setText('Connected')
                st_w.setFont(font)
            self.nearby_machines.setItem(i, 2, st_w)



        if machines:
            self.nearby_machines.setCurrentItem(self.nearby_machines.item(0,0))
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept(self):
        row = self.nearby_machines.currentRow()
        cur_ip = self.nearby_machines.item(row, 0)
        cur_host = self.nearby_machines.item(row, 1)
        self.chosen_machine = (cur_ip.text(), cur_host.text())
        super(ConnectToMachine, self).accept()


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],"t",['tray'])
    for opt, arg in opts:
        if opt in ('--tray'):
            os.system('obci_x_tray&')
    if checkpidfile('gui.pid'):
        sys.exit(0)

    app = QApplication([])
    p = QPixmap(os.path.join(settings.INSTALL_DIR, "gui/ugm/resources/obci+svarog.png"))
    s = QSplashScreen(p)
    s.show()
    s.showMessage("OpenBCI - free as in freedom.")
    dialog = ObciLauncherWindow()

    import sys
    dialog.start.connect(lambda name:sys.stderr.write('Start %s \n' % name))
    dialog.stop.connect(lambda name:sys.stderr.write('Stop %s \n' % name))
    s.finish(dialog)

    sys.exit(app.exec_())
