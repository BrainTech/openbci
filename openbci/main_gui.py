#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Łukasz Polak <l.polak@gmail.com>
#
"""This is main file for whole GUI part of OpenBCI - main window of whole
application, along with loading all needed modules GUIs"""

# We are using newer version of QVariant through our GUI, so we might as well
# set it here and let all hell loose on users of older versions of PyQT :)
import sip
sip.setapi('QVariant', 2)
import sys
from PyQt4 import QtCore, QtGui
from config.modules import MODULES_LIST

class BCIMainWindow(QtGui.QMainWindow):
    """Main window of the BCI application - shows list of available plugins and
    enables configuration of them"""
    
    def __init__(self, parent=None):
        super(BCIMainWindow, self).__init__(parent)
        # Holds all modules classes
        self.modules = {}
        # Loads modules from config into dictionary
        self.processModules(MODULES_LIST)
        # TODO: main gui should be made in designer, and not in code here
        self.setMinimumSize(800, 300)
        self.pluginsList = QtGui.QTreeWidget()
        self.pluginsList.setMinimumSize(50, 200)
        self.pluginsList.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.pluginsList.setHeaderLabels(["Nazwa"])
        for i_plugin in self.modules.values():
            l_item = QtGui.QTreeWidgetItem([i_plugin.name])
            l_item.plugin = i_plugin
            self.pluginsList.addTopLevelItem(l_item)
        self.pluginsList.setCurrentItem(None)
        self.connect(self.pluginsList, QtCore.SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"), self.itemChanged)
        
        # Dictionary for configuration widgets of modules
        self.dockWidgets = {}
        self.currentDockWidget = None
        self.setCentralWidget(self.pluginsList)
    
    def itemChanged(self, p_newItem):
        """Called, when selection on lists of plugins changes. Then it displays 
        configuration window for newly selected plugin, and closes old one, 
        unless it's floating.
        p_newItem (QTreeWidgetItem) - contains newly selected plugin
        p_oldItem (QTreeWidgetItem) - contains plugin that was selected
        before"""
        if self.currentDockWidget != None:
            # We remove widget only if it's not floating
            if not self.currentDockWidget.isFloating():
                self.removeDockWidget(self.currentDockWidget)
            else:
                self.currentDockWidget.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
            self.currentDockWidget = None
        
        if p_newItem != None:
            l_pluginName = p_newItem.plugin.name
            # If we haven't configured this plugin yet, we need to create its GUI
            if not self.dockWidgets.has_key(l_pluginName):
                self.dockWidgets[l_pluginName] = p_newItem.plugin.buildGui(self)
                self.dockWidgets[l_pluginName].setMinimumWidth(200)
            p_pluginDock = self.dockWidgets[l_pluginName]
            # We allow docking only on right side of window
            p_pluginDock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            # If dock was floating and closed before, we reset him into dock
            if not p_pluginDock.isVisible() and p_pluginDock.isFloating():
                p_pluginDock.setFloating(False)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, p_pluginDock)
            self.restoreDockWidget(p_pluginDock)
            self.currentDockWidget = p_pluginDock
    
    def processModules(self, p_modulesList):
        """Processes list with module names, and loads appropriate modules into
        program"""
        for i_moduleName in p_modulesList:
            self.processModule(i_moduleName)
    
    def processModule(self, p_moduleName):
        """Processes sing module with given name and load it into program"""
        # We are importing module from correct directory...
        l_bciModule = __import__("modules.%s.%s_module" % (p_moduleName, p_moduleName), fromlist=["modules.%s" % (p_moduleName)])
        # ...and then we create and save its main class into modules dictionary
        self.modules[p_moduleName] = eval("bci_module.%sModule()" % (p_moduleName.title()), {'bci_module' : l_bciModule})
    
if __name__ == "__main__":
    # We simply show main window
    APPLICATION = QtGui.QApplication(sys.argv)
    WINDOW = BCIMainWindow()
    WINDOW.show()
    sys.exit(APPLICATION.exec_())
