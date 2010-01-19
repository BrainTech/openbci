# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import xml.dom.minidom
import bci_plugin

class test_module_plugin(bci_plugin.BciBasePlugin):
	
	name =  u"Moduł testowy"
	
	def __init__(self):
		self.dockWidget = None
		
	def buildGui(self, p_parent):
		if self.dockWidget == None:
			self.dockWidget = TestModuleDockWidget(p_parent)
		return self.dockWidget
		
class TestModuleDockWidget(QDockWidget):
	
	def __init__(self, parent=None):
		QDockWidget.__init__(self, parent)
		self.setObjectName("TestModuleDockWidget")
		self.label = QLabel("Test")
		self.setWidget(self.label)