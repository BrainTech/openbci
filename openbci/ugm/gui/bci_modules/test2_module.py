# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.dom.minidom
import bci_plugin

class test2_module_plugin(bci_plugin.BciBasePlugin):
	
	name = u"Moduł testowy 2"
	
	def __init__(self):
		self.dockWidget = None
		
	def buildGui(self, p_parent):
		if self.dockWidget == None:
			self.dockWidget = TestModule2DockWidget(p_parent)
		return self.dockWidget
		
class TestModule2DockWidget(QDockWidget):
	
	def __init__(self, parent=None):
		QDockWidget.__init__(self, parent)
		self.setObjectName("TestModuleDockWidget")
		self.label = QLabel("Test2")
		self.setWidget(self.label)