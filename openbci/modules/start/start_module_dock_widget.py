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
from modules.start.start import Ui_Form
import os
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client 
import variables_pb2
import ConfigParser
import string

PATH = "/home/mrygacz/openbci/openbci/"


class StartModuleDockWidget(QtGui.QDockWidget):
    """Dock widget which is used to configure all UGM properties"""
    
    def __init__(self, parent=None):
        super(StartModuleDockWidget, self).__init__(parent)
	self.ui = Ui_Form()
        self.ui.setupUi(self)
	
	
	QtCore.QObject.connect(self.ui.VirtualAmplifier, QtCore.SIGNAL("clicked()"), self.startVirtualAmplifier)

	QtCore.QObject.connect(self.ui.Amplifier, QtCore.SIGNAL("clicked()"), self.startAmplifier)
	QtCore.QObject.connect(self.ui.Experiment, QtCore.SIGNAL("clicked()"), self.startExperiment)
	QtCore.QObject.connect(self.ui.Pokaz, QtCore.SIGNAL("clicked()"), self.startPokaz)
	QtCore.QObject.connect(self.ui.Demo, QtCore.SIGNAL("clicked()"), self.startDemo)

	QtCore.QObject.connect(self.ui.AddMonitor, QtCore.SIGNAL("clicked()"), self.addMonitor)
	QtCore.QObject.connect(self.ui.AddSpectrum, QtCore.SIGNAL("clicked()"), self.addSpectrum)
	QtCore.QObject.connect(self.ui.AddExperiment, QtCore.SIGNAL("clicked()"), self.addExperiment)
	QtCore.QObject.connect(self.ui.Stop, QtCore.SIGNAL("clicked()"), self.stop)

	self.Config = ConfigParser.ConfigParser()


    def startVirtualAmplifier(self):
	os.system("python " + PATH + "/start.py virtual_amplifier" )

    def startAmplifier(self):
	os.system("python " + PATH + "/start.py amplifier" )

    def startExperiment(self):
	os.system("python " + PATH + "/start.py experiment" )

    def startPokaz(self):
	os.system("python " + PATH + "/start.py pokaz" )

    def startDemo(self):
	os.system("python " + PATH + "/start.py demo" )



    def addMonitor(self):
	os.system("python " + PATH + "/start.py add_monitor" )

    def addSpectrum(self):
	os.system("python " + PATH + "/start.py add_spectrum" )

    def addExperiment(self):
	os.system("python " + PATH + "/start.py add_experiment" )

    def stop(self):
	os.system("killall screen" )


