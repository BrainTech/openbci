# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from modules.ugm.gui.UGMMain import Ui_UGMMainWidget
from modules.ugm.gui.ugm_properties_model import UGMPropertiesModel
from modules.ugm.gui.ugm_properties_delegate import UGMPropertiesDelegate
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client 
import variables_pb2

class UGMModuleDockWidget(QDockWidget):
    def __init__(self, p_configManager, parent=None):
        super(UGMModuleDockWidget, self).__init__(parent)
        self.configManager = p_configManager
        self.ui = Ui_UGMMainWidget()
        self.ui.setupUi(self)
        l_attributesConfig = self.configManager.get_attributes_config()
        self.propertiesModel = UGMPropertiesModel(l_attributesConfig['attributes_def'], 
                                                  l_attributesConfig['attributes_for_elem'], 
                                                  self.configManager.get_ugm_fields())
        self.propertiesDelegate = UGMPropertiesDelegate()
        self.ui.propertyList.setModel(self.propertiesModel)
        self.ui.propertyList.setItemDelegate(self.propertiesDelegate)
        self.ui.propertyList.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.resizeColumns()
        self.connect(self.ui.propertyList, SIGNAL("collapsed(QModelIndex)"), self.resizeColumns)
        self.connect(self.ui.propertyList, SIGNAL("expanded(QModelIndex)"), self.resizeColumns)
        
        self.initActions()
        self.ui.propertyList.selectionModel().selectionChanged.connect(self.updateActions)
        
        self._connection = None
    
    def resizeColumns(self, p_index=None):
        for i_column in range(self.propertiesModel.columnCount(QModelIndex())):
            self.ui.propertyList.resizeColumnToContents(i_column)
    
    def initActions(self):
        self.ui.saveButton.setDefaultAction(self.ui.actionSave)
        self.ui.addButton.setDefaultAction(self.ui.actionAdd)
        self.ui.addRectangleButton.setDefaultAction(self.ui.actionAddRectangle)
        self.ui.addImageButton.setDefaultAction(self.ui.actionAddImage)
        self.ui.addTextButton.setDefaultAction(self.ui.actionAddText)
        self.ui.removeButton.setDefaultAction(self.ui.actionRemove)
        
        self.ui.actionSave.triggered.connect(self.saveConfig)
        self.ui.actionAdd.triggered.connect(lambda p_unused, p_type="field": self.addRoot(p_type))
        self.ui.actionAddRectangle.triggered.connect(lambda p_unused, p_type="rectangle": self.addRoot(p_type))
        self.ui.actionAddImage.triggered.connect(lambda p_unused, p_type="image": self.addRoot(p_type))
        self.ui.actionAddText.triggered.connect(lambda p_unused, p_type="text": self.addRoot(p_type))
        self.ui.actionRemove.triggered.connect(self.removeRoot)
        
        self.updateActions()    
    
    def updateActions(self):
        # We can always add new field
        self.ui.actionAdd.setEnabled(True)
        
        l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        if not self.ui.propertyList.selectionModel().selection().isEmpty() and l_currentIndex.isValid():
            l_item = self.propertiesModel.getItem(l_currentIndex)
            l_canRemove = (l_item.type == 'field' or l_item.type == 'rectangle' or l_item.type == 'image' or l_item.type == 'text')
            l_canAdd = (l_item.type == 'list')
            self.ui.actionAddRectangle.setEnabled(l_canAdd)
            self.ui.actionAddImage.setEnabled(l_canAdd)
            self.ui.actionAddText.setEnabled(l_canAdd)
            self.ui.actionRemove.setEnabled(l_canRemove)
        else:
            self.ui.actionAddRectangle.setEnabled(False)
            self.ui.actionAddImage.setEnabled(False)
            self.ui.actionAddText.setEnabled(False)
            self.ui.actionRemove.setEnabled(False)
    
    def saveConfig(self):
        self.configManager.set_full_config(self.propertiesModel.createConfigNode())
        if self.propertiesModel.structureModified:
            l_type = 0
            self.propertiesModel.structureModified = False
        else:
            l_type = 1
        l_msg = variables_pb2.UgmUpdate()
        l_msg.type = int(l_type)
        l_msg.value = self.configManager.config_to_message()
        if not self._connection:
            self._connection = connect_client(type = peers.LOGIC)
        
        self._connection.send_message(
            message = l_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)
        
        # We also save new config to file
        self.configManager.update_to_file('new_config')
    
    def addRoot(self, p_type):
        print "Add " + p_type
        l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        self.propertiesModel.addRoot(l_currentIndex, p_type) 
        
    def removeRoot(self):
        print "Remove"
        l_currentIndex = self.ui.propertyList.selectionModel().currentIndex()
        self.propertiesModel.removeRoot(l_currentIndex.parent(), l_currentIndex.row())