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
from obci_launcher import Ui_ObciLauncher

from obci_launcher_engine import OBCILauncherEngine
import launcher.obci_script as obci_script

class ObciLauncherDialog(QDialog, Ui_ObciLauncher):
    '''
    classdocs
    '''
    start = Signal(str)
    stop = Signal(str)
    reset = Signal(str)
    

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ObciLauncherDialog, self).__init__(parent)
        self.setupUi(self)
        self.scenarios.horizontalHeader().setResizeMode (QHeaderView.ResizeMode.Stretch)
        self.scenarios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scenarios.setColumnCount(3)
        self.scenarios.setHorizontalHeaderLabels(["Scenario", "Path", "Status"])
        self.scenarios.horizontalHeader().setVisible(True)
        self.scenarios.currentCellChanged.connect(self._setInfo)
        self.parameters.setHeaderLabels(["Name", 'Value'])
        self.parameters.itemClicked.connect(self._itemClicked)
        self.parameters.setColumnWidth(0, 200)

        self.start_button.clicked.connect(self._start)
        self.stop_button.clicked.connect(self._stop)
        self.reset_button.clicked.connect(self._reset)

        self._params = []
        self._scenarios = []

        client = obci_script.client_server_prep()
        self.engine = OBCILauncherEngine(client)
        self.engine.update_ui.connect(self.update_user_interface)

    def setScenarios(self, scenarios):
        self._scenarios = scenarios
        self.scenarios.clearContents()
        self.scenarios.setRowCount(len(scenarios))
        for i, s in enumerate(scenarios):
            name = QTableWidgetItem(s['name'])
            self.scenarios.setItem(i, 0, name)
            path = QTableWidgetItem(s['path'])
            self.scenarios.setItem(i, 1, path)            
            status = QTableWidgetItem(s['status'])
            self.scenarios.setItem(i, 2, status)
            if 'bg' in s:
                name.setBackground(QColor(s['bg']))
                status.setBackground(QColor(s['bg']))
            if 'tooltip' in s:
                name.setToolTip(s['tooltip'])
                status.setToolTip(s['tooltip'])
    
    def getScenarios(self):
        self._scenarios[self.scenarios.currentRow()]['params'] = self._getParams()
        return self._scenarios

    def _setParams(self, params):
        expanded = set()
        for i in range(self.parameters.topLevelItemCount()):
            item = self.parameters.topLevelItem(i)
            if item.isExpanded(): expanded.add(item.text(0))
        self.parameters.clear()
        self._params = params
        for section in params:
            parent = QTreeWidgetItem([section['name']])
            parent.setFirstColumnSpanned(True)
            self.parameters.addTopLevelItem(parent)
            if unicode(parent.text(0)) in expanded:
                parent.setExpanded(True)
            if 'tooltip' in section:
                parent.setToolTip(0, section['tooltip'])
            for j, param in enumerate(section['params']):
                child = QTreeWidgetItem([param['name'], param['value']])                
                parent.addChild(child)
                if 'tooltip' in param:
                    child.setToolTip(0, param['tooltip'])
                if 'valtooltip' in param:
                    child.setToolTip(1, param['valtooltip'])
                else:
                    child.setToolTip(1, child.toolTip(0))
    def _getParams(self):
        for i, section in enumerate(self._params):
            parent = self.parameters.topLevelItem(i)
            for j, param in enumerate(section['params']):
                child = parent.child(j)
                param['value'] = child.text(1)
        return self._params

    def _itemClicked(self, item, column):
        if item.columnCount() > 1 and column > 0:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        else:
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    
    def _setInfo(self, curRow, curCol, lastRow, lastCol):
        print curRow, lastRow
        if curRow == lastRow:
            return
        self.info.setText(self._scenarios[curRow].get('info', ''))
        if lastRow >= 0:
            self._scenarios[lastRow]['params'] = self._getParams()
        self._setParams(self._scenarios[curRow]['params'])
        self.parameters_of.setTitle("Parameters of " + self._scenarios[curRow]['name'])
    
    def _start(self):
        self.start.emit(self._scenarios[self.scenarios.currentRow()]['name'])
    def _stop(self):
        self.stop.emit(self._scenarios[self.scenarios.currentRow()]['name'])
    def _reset(self):
        self.reset.emit(self._scenarios[self.scenarios.currentRow()]['name'])

    def update_user_interface(self, update_msg):
        print "!!!!!!!updating user interface", update_msg
        

if __name__ == '__main__':
    app = QApplication([])
    dialog = ObciLauncherDialog()
    scenarios = dialog.engine.list_experiments()
    # scenarios = [{'name':'scenario1', 'status':'running', 'tooltip':u'Przejęcie kontroli nad światem', 'bg':'green', 'info':u"Zarabiamy, kase budujemy armie i <b>PODBIJAMY ŚWIAT</b>"}, \
    #              {'name':'scenario2', 'status':'stopped', 'tooltip':u'Studiowanie', 'bg':'red', "info":"Imprezujemy do rana!"}, \
    #              {'name':'scenario3', 'status':'launching', 'tooltip':u'Imreza!!!!', 'bg':'yellow'}]
    params = [{'name':'amplifier', 'tooltip':'Amplifier params', 'params':[
                                                                           {'name':'sampling_rate', 'value':'128', 'tooltip':'Sampling Rate', 'valtooltip':u"wielokrotność 128"}, \
                                                                           {'name':'device_path', 'value':'/dev/tmsi0', 'tooltip':u'Adres urządzenia', 'valtooltip':u'np. /dev/tmsi0'}, \
                                                                           {'name':'type', 'value':'d', 'tooltip':u'Typ urządzenia', 'valtooltip':u'(d- usb,b-bluetooth,i-ip)'}]}, \
              {'name':'dupa', 'params':[{'name':'kupa', 'value':'rzadka', 'tooltip':'Zdrowa lub rzadka'}]}]
    from copy import deepcopy
    #scenarios[0]['params'] = params
    # scenarios[1]['params'] = deepcopy(params)
    # scenarios[2]['params'] = deepcopy(params)
    dialog.setScenarios(scenarios)
    import sys
    dialog.start.connect(lambda name:sys.stderr.write('Start %s \n' % name))
    dialog.stop.connect(lambda name:sys.stderr.write('Stop %s \n' % name))
    dialog.reset.connect(lambda name:sys.stderr.write('Reset %s \n' % name))

    dialog.engine.update_ui.emit("aaaaaa")

    dialog.exec_()
    print dialog.getScenarios()
        
