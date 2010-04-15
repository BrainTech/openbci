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
from modules.ugm.gui.UGMMain import Ui_UGMMainWidget
from modules.ugm.gui.ugm_properties_model import UGMPropertiesModel
from modules.ugm.gui.ugm_properties_delegate import UGMPropertiesDelegate
from ugm.ugm_config_manager import UgmConfigManager
import os
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client 
import variables_pb2

class UGMModuleDockWidget(QtGui.QDockWidget):
    """Dock widget which is used to configure all UGM properties"""
    
    def __init__(self, p_configManager, parent=None):
        super(UGMModuleDockWidget, self).__init__(parent)
        self.fileName = None
        self.configManager = p_configManager
        # UI auto-generated from QT Designer
        self.ui = Ui_UGMMainWidget()
        self.ui.setupUi(self)
        l_attributesConfig = self.configManager.get_attributes_config()
        self._initModel(UGMPropertiesModel(l_attributesConfig['attributes_def'], 
                                           l_attributesConfig['attributes_for_elem'], 
                                           self.configManager.get_ugm_fields()))
        
        self.connect(self.ui.propertyList, QtCore.SIGNAL("collapsed(QModelIndex)"), self.resizeColumns)
        self.connect(self.ui.propertyList, QtCore.SIGNAL("expanded(QModelIndex)"), self.resizeColumns)
        self.initActions()
        self._connection = None
    
    def resizeColumns(self):
        """Resizes columns, to fit contents"""
        for i_column in range(self.propertiesModel.columnCount(QtCore.QModelIndex())):
            self.ui.propertyList.resizeColumnToContents(i_column)
    
    def initActions(self):
        """Initialises all actions used by UGM dock widget"""
        self.ui.sendToUgmButton.setDefaultAction(self.ui.actionSendToUgm)
        self.ui.loadButton.setDefaultAction(self.ui.actionLoad)
        self.ui.saveButton.setDefaultAction(self.ui.actionSave)
        self.ui.saveAsButton.setDefaultAction(self.ui.actionSaveAs)
        self.ui.addButton.setDefaultAction(self.ui.actionAdd)
        self.ui.addRectangleButton.setDefaultAction(self.ui.actionAddRectangle)
        self.ui.addImageButton.setDefaultAction(self.ui.actionAddImage)
        self.ui.addTextButton.setDefaultAction(self.ui.actionAddText)
        self.ui.removeButton.setDefaultAction(self.ui.actionRemove)
        
        self.ui.actionSendToUgm.triggered.connect(self.sendToUgm)
        self.ui.actionLoad.triggered.connect(self.loadConfig)
        self.ui.actionSave.triggered.connect(self.saveConfig)
        self.ui.actionSaveAs.triggered.connect(self.saveConfigAs)
        self.ui.actionAdd.triggered.connect(lambda p_unused, p_type="field": self.addRoot(p_type))
        self.ui.actionAddRectangle.triggered.connect(lambda p_unused, p_type="rectangle": self.addRoot(p_type))
        self.ui.actionAddImage.triggered.connect(lambda p_unused, p_type="image": self.addRoot(p_type))
        self.ui.actionAddText.triggered.connect(lambda p_unused, p_type="text": self.addRoot(p_type))
        self.ui.actionRemove.triggered.connect(self.removeRoot)
        
        self.updateActions()    
    
    def updateActions(self, p_newSelection=None):
        """Called every time something happens, that can change availability of
        this plugins actions"""
        # If this was called by signal, we will have new selection send as parameter
        if p_newSelection != None and p_newSelection.count() > 0 and p_newSelection.first().isValid():
            l_currentIndex = p_newSelection.first().topLeft()
        else:
            l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        # We can always add new field, sen to ugm or save/load
        self.ui.actionAdd.setEnabled(True)
        self.ui.actionSendToUgm.setEnabled(True)
        self.ui.actionLoad.setEnabled(True)
        self.ui.actionSave.setEnabled(True)
        self.ui.actionSaveAs.setEnabled(True)
        
        
        if not self.ui.propertyList.selectionModel().selection().isEmpty() and l_currentIndex.isValid():
            l_item = self.propertiesModel.getItem(l_currentIndex)
            # We can only remove fields or stimuluses...
            l_canRemove = (l_item.type == 'field' or l_item.type == 'rectangle' or l_item.type == 'image' or l_item.type == 'text')
            # ...and we can only add stimuluses to lists
            l_canAddStimulus = (l_item.type == 'list')
            self.ui.actionAddRectangle.setEnabled(l_canAddStimulus)
            self.ui.actionAddImage.setEnabled(l_canAddStimulus)
            self.ui.actionAddText.setEnabled(l_canAddStimulus)
            self.ui.actionRemove.setEnabled(l_canRemove)
        else:
            # Nothing is selected, so we can't add or remove anything :)
            self.ui.actionAddRectangle.setEnabled(False)
            self.ui.actionAddImage.setEnabled(False)
            self.ui.actionAddText.setEnabled(False)
            self.ui.actionRemove.setEnabled(False)
    
    def sendToUgm(self):
        """Sends currently edited config to UGM, if it's running"""
        # # Change config managers loaded config
        self.configManager.set_full_config(self.propertiesModel.createConfigNode())
        # # We check whether we changed model structure: added or removed fields,
        # # changed ids, because if we did then we must send different message type
        if self.propertiesModel.structureModified:
            l_type = 0
            self.propertiesModel.structureModified = False
        else:
            l_type = 1
        l_msg = variables_pb2.UgmUpdate()
        l_msg.type = int(l_type)
        l_msg.value = self.configManager.config_to_message()
        #     
        # # Everything done :) All that is left is to establish connection if needed...
        if not self._connection:
            self._connection = connect_client(type = peers.LOGIC)
         # ...and send message to UGM
        self._connection.send_message(
            message = l_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)
        
        #### TEMPORARY FOR LOCAL UGM ####
        #l_tempConfigManager = UgmConfigManager()
        #l_tempConfigManager.set_full_config(self.propertiesModel.createConfigNode())
        #l_tempConfigManager.update_to_file()
        
    
    def loadConfig(self):
        """Loads config from file and rebuilds whole tree"""
        l_fileName = QtGui.QFileDialog().getOpenFileName(self, self.tr(u"Otwórz"), QtCore.QString(), "Pliki UGMa (*.ugm)")
        if l_fileName == "": 
            return    
        self.fileName = unicode(l_fileName)
        l_shortFileName = os.path.split(unicode(l_fileName))[1]
        self.setWindowTitle(QtGui.QApplication.translate("UGMMainWidget", "UGM Configuration - %s" % (l_shortFileName), None, QtGui.QApplication.UnicodeUTF8))
        
        self.configManager.update_from_file(self.fileName)
        l_attributesConfig = self.configManager.get_attributes_config()
        self._initModel(UGMPropertiesModel(l_attributesConfig['attributes_def'], 
                                             l_attributesConfig['attributes_for_elem'], 
                                             self.configManager.get_ugm_fields()))
        
    
    def saveConfig(self):
        """Saves config to default file, if none were loaded or to last loaded file"""
        # Change config managers loaded config
        self.configManager.set_full_config(self.propertiesModel.createConfigNode())
        
        # We also save new config to file
        self.configManager.update_to_file(self.fileName)
        
    def saveConfigAs(self):
        """Saves config to specified file"""
        l_fileName = QtGui.QFileDialog().getSaveFileName(self, self.tr("Zapisz jako..."), QtCore.QString(), "Plik UGMa (*.ugm)")
        if l_fileName == "": 
            return
        self.fileName = l_fileName
        
        self.saveConfig()
    
    def addRoot(self, p_type):
        """Adds root item of given type to the list/model"""
        l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        self.propertiesModel.addRoot(l_currentIndex, p_type)
        self.updateActions()
        
    def removeRoot(self):
        """Removes currently selected root item from list/model"""
        l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        self.propertiesModel.removeRoot(l_currentIndex.parent(), l_currentIndex.row())
        self.updateActions()
        
    def _initModel(self, p_model):
        """Creates and initialises model, from given parameter"""
        self.propertiesModel = p_model
        self.propertiesDelegate = UGMPropertiesDelegate()
        # Preparing model
        self.ui.propertyList.setModel(self.propertiesModel)
        self.ui.propertyList.setItemDelegate(self.propertiesDelegate)
        self.ui.propertyList.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        # Initialising everything
        self.resizeColumns()
        self.ui.propertyList.selectionModel().selectionChanged.connect(self.updateActions)
