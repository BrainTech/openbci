# -*- coding: utf-8 -*-

from abc import abstractmethod
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class BciBasePlugin:
	
	name = ""
	
	@abstractmethod
	def buildGui(self):
		raise NotImplementedError, "Should be implemented in subclasses"