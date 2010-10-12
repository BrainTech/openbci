# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
"""Dock widget for configuring UGM"""

from PyQt4 import QtCore, QtGui
from modules.exp.test import Ui_Form
import os
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client 
import variables_pb2
import ConfigParser
import string

class EXPModuleDockWidget(QtGui.QDockWidget):
    """Dock widget which is used to configure all UGM properties"""
    
    def __init__(self, parent=None):
        super(EXPModuleDockWidget, self).__init__(parent)
	self.ui = Ui_Form()
        self.ui.setupUi(self)
	self.setValues("initial")
	QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.showInput)
	QtCore.QObject.connect(self.ui.pushButton_2, QtCore.SIGNAL("clicked()"), self.addRow)
	QtCore.QObject.connect(self.ui.pushButton_3, QtCore.SIGNAL("clicked()"), self.loadConfig)
	QtCore.QObject.connect(self.ui.toolButton, QtCore.SIGNAL("clicked()"), self.loadConfig)
	#QtCore.QObject.connect(self.ui.lineEdit, QtCore.SIGNAL("returnPressed()"), self.showInput)
	self.Config = ConfigParser.ConfigParser()
	#self.Config.read("/home/mrygacz/openbci/openbci/openbci/modules/exp/config.ini")
	#print self.Config.sections()


    def addRow(self):
	print "insert row"
	self.ui.tableWidget.insertRow(0) 
	#self.ui.tableWidget.insertRow(1) 

	#self.ui.tableWidget.insertRow(2) 

    def showInput(self):
    	print "show input: %s" % str(self.ui.textEdit.toPlainText())
	print "table: %s" % str(self.ui.tableWidget.itemAt(0,0).text())

    def setValues(self, text):
	self.ui.textEdit.setPlainText(text)
         
    def loadConfig(self):
        """Loads config from file and rebuilds whole tree"""
        l_fileName = QtGui.QFileDialog().getOpenFileName(self, self.tr(u"Otwórz"), QtCore.QString(), "*")
        if l_fileName == "": 
            return    
        self.fileName = unicode(l_fileName)
        l_shortFileName = os.path.split(unicode(l_fileName))[1]
        self.setWindowTitle("test")
	print "filename: ", l_fileName
        #f = open(l_fileName)
	#print f.readlines()
	
        #Config = ConfigParser.ConfigParser()
	self.Config.read("/home/mrygacz/openbci/openbci/openbci/modules/exp/config.ini")
	
	for section in self.Config.sections():
	    print section

	self.ui.textEdit.setPlainText(self.Config.get("Book","title"))

    
       
    def saveConfigAs(self):
        """Saves config to specified file"""
        l_fileName = QtGui.QFileDialog().getSaveFileName(self, self.tr("Zapisz jako..."), QtCore.QString(), "Plik UGMa (*.ugm)")
        if l_fileName == "": 
            return
        self.fileName = l_fileName
        
        self.saveConfig()

