# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from modules.ugm.gui.ugm_tree_element import NAME, VALUE
from modules.ugm.gui.ugm_properties_root import UGMPropertiesRoot
from modules.ugm.gui.ugm_property import UGMProperty

class UGMPropertiesModel(QAbstractItemModel):
    
    def __init__(self, p_attributes, p_attributesForElements, p_data, parent=None):
        super(UGMPropertiesModel, self).__init__(parent)
        self.loadAttributeTypes(p_attributes)
	print p_attributesForElements
        self.setAttributeSubtypes()
        self.setAttributesForElements(p_attributesForElements)
        self.rootItem = self.createRoot(p_data, 'fields', 'Root')
        self.structureModified = True
         # TODO: setFirstColumnSpanned na rootach
    
    
    def createConfigNode(self):
        return self.rootItem.createConfigNode()
    
    
    def loadAttributeTypes(self, p_attributes):
        self.attributeTypes = {}
        for i_attributeName, i_attributeParameters in p_attributes.items():
            self.attributeTypes[i_attributeName] = self.getAttributeType(i_attributeParameters)
    
    
    def getAttributeType(self, p_attributeParameters):
        l_value = p_attributeParameters['value']
        if isinstance(l_value, list):
            # List means, that we have either enumerated type or something depending on other attribute
            if 'depend_from' in p_attributeParameters:
                l_attributeType = \
                    {'type': 'dependent', 
                    'parameters' :
                        {'depends_on': p_attributeParameters['depend_from'],
                        'subtypes': l_value},
                    'default': None
                    }
            else:
                # Enumerated type
                l_attributeType = \
                    {'type': 'enumerated',
                    'parameters':
                        {'values': l_value},
                    'default':l_value[0]
                    }
        else:
            # Simple type
            l_attributeType = {'type': l_value, 'parameters': None, 'default' : 0}
        
        return l_attributeType
    
        
    def setAttributeSubtypes(self):
        for i_attributeType in self.attributeTypes.values():
            if i_attributeType['type'] == 'dependent':
                l_subtypes = {}
                for (i_value, i_subtype) in zip(self.attributeTypes[i_attributeType['parameters']['depends_on']]['parameters']['values'], i_attributeType['parameters']['subtypes']):
                    # We create fake attribute to give to this function, because subtypes can only be simple/enumerated
                    l_subtypes[i_value] = self.getAttributeType({'value': i_subtype})
                i_attributeType['parameters']['subtypes'] = l_subtypes
    
    def setAttributesForElements(self, p_attributesForElements):
        self.stimulusAttributes = {}
        for i_elementName, i_attributes in p_attributesForElements.items():
            if i_elementName == 'field':
                self.fieldAttributes = i_attributes
            else:
                self.stimulusAttributes[i_elementName] = i_attributes
    
    def createRoot(self, p_subitems, p_subitems_type, p_name):
        l_root = UGMPropertiesRoot(p_name, 'list')
        for i_subitem in p_subitems:
            p_subItemsRoot = self.createFieldsRoot(i_subitem, p_subitems_type)
            l_root.addChild(p_subItemsRoot)
        l_root.setupDependents()
        return l_root
    
    def createFieldsRoot(self, p_field, p_subitems_type):
        if (p_subitems_type == 'fields'):
            l_rootName = 'Pole'
            l_type = 'field'
            l_attributes = self.fieldAttributes
        else: # stimuluses
            l_type = p_field['stimulus_type']
            l_rootName = 'Bodziec (typ: ' + l_type + ')'
            l_attributes = self.stimulusAttributes[l_type]
        
        l_root = UGMPropertiesRoot(l_rootName, l_type)
        p_property = UGMProperty('id', p_field['id'], 'int', {})
        for i_attributeName in l_attributes:
            p_property = UGMProperty(i_attributeName, p_field[i_attributeName], self.attributeTypes[i_attributeName]['type'], self.attributeTypes[i_attributeName]['parameters'])
            l_root.addChild(p_property)
        if 'stimuluses' in p_field:
            p_stimulusesRoot = self.createRoot(p_field['stimuluses'], 'stimuluses', 'stimuluses')
            l_root.addChild(p_stimulusesRoot)
        l_root.setupDependents()
        return l_root
    
    def addRoot(self, p_parentIndex, p_type):
        self.structureModified = True
        if p_type == 'field':
            l_parentIndex = QModelIndex()
            l_parent = self.rootItem
        else:
            l_parentIndex = p_parentIndex
            l_parent = self.getItem(p_parentIndex)
        l_newRoot = self.createEmptyRoot(p_type)
        self.beginInsertRows(l_parentIndex, l_parent.childCount(), l_parent.childCount())
        l_parent.addChild(l_newRoot)
        self.endInsertRows()
        
    def createEmptyRoot(self, p_type):
        if p_type == 'field':
            l_attributes = self.fieldAttributes
            l_rootName = 'Pole'
        else:
            l_attributes = self.stimulusAttributes[p_type]
            l_rootName = 'Bodziec (typ: ' + p_type + ')'
            
        l_root = UGMPropertiesRoot(l_rootName, p_type)
        p_property = UGMProperty('id', 0, 'int', {})
        for i_attributeName in l_attributes:
            p_property = UGMProperty(i_attributeName, self.attributeTypes[i_attributeName]['default'], self.attributeTypes[i_attributeName]['type'], self.attributeTypes[i_attributeName]['parameters'])
            l_root.addChild(p_property)
        p_stimulusesRoot = UGMPropertiesRoot('stimuluses', 'list')
        l_root.addChild(p_stimulusesRoot)
        l_root.setupDependents()
        return l_root
        
    def removeRoot(self, p_parentIndex, p_position):
        self.structureModified = True
        l_parentItem = self.getItem(p_parentIndex)

        self.beginRemoveRows(p_parentIndex, p_position, p_position)
        success = l_parentItem.removeChild(p_position)
        self.endRemoveRows()
    
    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        return parentItem.childCount()
    
    def columnCount(self, parent=QModelIndex()):
        return 2
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        else:
            item = self.getItem(index)
            if item.editable(index.column()):
                return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        column = index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == NAME:
                return self.getItem(index).data(NAME)
            elif column == VALUE:
                return self.getItem(index).data(VALUE)
        
        return None
    
    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False
        
        item = self.getItem(index)
        result = item.setData(index.column(), value)
        
        if result:
            if item.name == 'id':
                self.structureModified = True
            if item.hasDependents():
                # Since potentially some other children values changed, we refresh all of them
                l_parent = self.getItem(index.parent())
                self.dataChanged.emit(index.parent().child(0, VALUE), index.parent().child(l_parent.childCount() - 1, VALUE))
            else:
                self.dataChanged.emit(index, index)
        
        return result
    
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        
        childItem = self.getItem(index)
        parentItem = childItem.parent()
        
        if parentItem == self.rootItem:
            return QModelIndex()
        
        return self.createIndex(parentItem.childNumber(), 0, parentItem)
    
    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()
        
        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
    
    def getItem(self, index):
        """
        Returns item, that is pointed by given QModelIndex.
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        
        return self.rootItem
