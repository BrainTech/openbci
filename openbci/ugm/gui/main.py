# -*- coding: utf-8 -*-

import sip
sip.setapi('QVariant', 2)

import os
import imp
import sys
import platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.dom.minidom as xml_dom
import time

APP_DIR = os.getcwd() + '/'

class BCIMainWindow(QMainWindow):
	"""Main window of the BCI application - shows list of available plugins and enables configuration of them"""
	
	def __init__(self, parent=None):
		super(BCIMainWindow, self).__init__(parent)
		self.modules = {}
		self.process_config_xml(xml_dom.parse(APP_DIR + "config/config.xml"))
		
		self.setMinimumSize(600,450)
		self.pluginsList = QTreeWidget()
		self.pluginsList.setMinimumSize(200,200)
		self.pluginsList.setContextMenuPolicy(Qt.ActionsContextMenu)
		self.pluginsList.setHeaderLabels(["Nazwa"])
		for i_plugin in self.modules.values():
			l_item = QTreeWidgetItem([i_plugin.name])
			l_item.plugin = i_plugin
			self.pluginsList.addTopLevelItem(l_item)
		self.pluginsList.setCurrentItem(None)
		self.connect(self.pluginsList, SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.itemChanged)
		
		self.dockWidgets = {}
		self.currentDockWidget = None
		self.setCentralWidget(self.pluginsList)
	
	def itemChanged(self, p_newItem, p_oldItem):
		"""Called, when selection on lists of plugins changes
		p_newItem (QTreeWidgetItem) - contains newly selected plugin
		p_oldItem (QTreeWidgetItem) - contains plugin that was selected before"""
		if self.currentDockWidget != None:
			if not self.currentDockWidget.isFloating():
				self.removeDockWidget(self.currentDockWidget)
			else:
				self.currentDockWidget.setAllowedAreas(Qt.NoDockWidgetArea)
			self.currentDockWidget = None
		
		if p_newItem != None:
			l_pluginName = p_newItem.plugin.name
			if not self.dockWidgets.has_key(l_pluginName):
				self.dockWidgets[l_pluginName] = p_newItem.plugin.buildGui(self)
				self.dockWidgets[l_pluginName].setMinimumWidth(200)
			p_pluginDock = self.dockWidgets[l_pluginName]
			p_pluginDock.setAllowedAreas(Qt.RightDockWidgetArea)
			if not p_pluginDock.isVisible() and p_pluginDock.isFloating():
				p_pluginDock.setFloating(False)
			self.addDockWidget(Qt.RightDockWidgetArea, p_pluginDock)
			self.restoreDockWidget(p_pluginDock)
			self.currentDockWidget = p_pluginDock
	
	def process_config_xml(self, p_xml):
		"""Processes configuration xml and load information into program"""
		for i_main_element in p_xml.getElementsByTagName('modules'):
			self.process_modules_xml(i_main_element)
	
	def process_modules_xml(self, p_xml):
		"""Processes 'module' tag from configuration xml"""
		for i_module_element in p_xml.getElementsByTagName('module'):
			l_module_name = i_module_element.attributes['name'].value
			(l_file, l_filename, l_data) = imp.find_module(l_module_name, ['bci_modules/'])
			l_bci_module = imp.load_module(l_module_name, l_file, l_filename, l_data)
			self.modules[l_module_name] = eval("bci_module.%s_plugin()" % (l_module_name), {'bci_module' : l_bci_module})
	
def main():
	app = QApplication(sys.argv)
	window = BCIMainWindow()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()