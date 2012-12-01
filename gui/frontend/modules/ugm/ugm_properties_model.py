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
"""Defines model of UGM properties"""

from PyQt4 import QtCore
from obci.gui.frontend.modules.ugm.ugm_tree_element import NAME, VALUE
from obci.gui.frontend.modules.ugm.ugm_properties_root import UGMPropertiesRoot
from obci.gui.frontend.modules.ugm.ugm_property import UGMProperty

class UGMPropertiesModel(QtCore.QAbstractItemModel):
    """Defines model of UGM properties"""
    def __init__(self, p_attributes, p_attributesForElements, p_data, parent=None):
        super(UGMPropertiesModel, self).__init__(parent)
        self.attributeTypes = {}
        self.stimulusAttributes = {}
        self.fieldAttributes = []
        self.loadAttributeTypes(p_attributes)
        self.setAttributeSubtypes()
        self.setAttributesForElements(p_attributesForElements)
        self.rootItem = self.createRoot(p_data, 'fields', 'Root')
        self.structureModified = True
        # TODO: należy użyć setFirstColumnSpanned na korzeniach drzewa, żeby rozpinały się one na
        # dwa pola i ładnie to wyglądało:)
    
    def createConfigNode(self):
        """Creates list in format, that is understood by UgmConfigManager"""
        return self.rootItem.createConfigNode()
    
    def loadAttributeTypes(self, p_attributes):
        """Loads attribute types, from given list. Usually they come from 
        UgmConfigManager"""
        for i_attributeName, i_attributeParameters in p_attributes.items():
            self.attributeTypes[i_attributeName] = self.getAttributeType(i_attributeParameters)
    
    def getAttributeType(self, p_attributeParameters):
        """Processes single parameter entry that we got from parameter types
        list and makes it usable by properties model"""
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
            if l_value == 'int' or l_value == 'float':
                l_default = 0
            elif l_value == 'color':
                l_default = '#000000'
            elif l_value == 'font':
                l_default = 'Liberation Mono'
            elif l_value == 'string':
                l_default = ''
            else:
                l_default = None
            l_attributeType = {'type': l_value, 'parameters': None, 'default' : l_default}
        
        return l_attributeType
        
    def setAttributeSubtypes(self):
        """Sets subtypes of attributes for those attributes, that are dependent
        on other attributes"""
        for i_attributeType in self.attributeTypes.values():
            if i_attributeType['type'] == 'dependent':
                l_subtypes = {}
                for (i_value, i_subtype) in zip(self.attributeTypes[i_attributeType['parameters']['depends_on']]['parameters']['values'], 
                                                                    i_attributeType['parameters']['subtypes']):
                    # We create fake attribute to give to this function, because subtypes can only be simple/enumerated
                    # so we are sure that it will be allright
                    l_subtypes[i_value] = self.getAttributeType({'value': i_subtype})
                i_attributeType['parameters']['subtypes'] = l_subtypes
    
    def setAttributesForElements(self, p_attributesForElements):
        """Remembers, which element (stimulus or field) requires which 
        attributes, usually given from UgmConfigManager"""
        for i_elementName, i_attributes in p_attributesForElements.items():
            if i_elementName == 'field':
                self.fieldAttributes = i_attributes
            else:
                self.stimulusAttributes[i_elementName] = i_attributes
    
    def createRoot(self, p_subitems, p_subitems_type, p_name):
        """Creates single list root in properites model. This root contains
        stimuluses or fields
        This function is used when recreating model from configuration file."""
        l_root = UGMPropertiesRoot(p_name, 'list')
        for i_subitem in p_subitems:
            p_subItemsRoot = self.createFieldsRoot(i_subitem, p_subitems_type)
            l_root.addChild(p_subItemsRoot)
        l_root.setupDependents()
        return l_root
    
    def createFieldsRoot(self, p_field, p_subitems_type):
        """Create single fields root in properties model. This root represents
        either field or stimulus, and contains its attributes.
        This function is used when recreating model from configuration file."""
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
            p_property = UGMProperty(i_attributeName, p_field[i_attributeName], 
                                     self.attributeTypes[i_attributeName]['type'], 
                                     self.attributeTypes[i_attributeName]['parameters'])
            l_root.addChild(p_property)
        if 'stimuluses' in p_field:
            p_stimulusesRoot = self.createRoot(p_field['stimuluses'], 'stimuluses', 'stimuluses')
            l_root.addChild(p_stimulusesRoot)
        l_root.setupDependents()
        return l_root
    
    def addRoot(self, p_parentIndex, p_type):
        """Add single element - field or stimulus - to already created model."""
        self.structureModified = True
        if p_type == 'field':
            # Field has root as parent, which is empty index
            l_parentIndex = QtCore.QModelIndex()
            l_parent = self.rootItem
        else:
            l_parentIndex = p_parentIndex
            l_parent = self.getItem(p_parentIndex)
        l_newRoot = self.createEmptyRoot(p_type)
        self.beginInsertRows(l_parentIndex, l_parent.childCount(), l_parent.childCount())
        l_parent.addChild(l_newRoot)
        self.endInsertRows()
        
    def createEmptyRoot(self, p_type):
        """Creates empty root of given type to be inserted into model."""
        if p_type == 'field':
            l_attributes = self.fieldAttributes
            l_rootName = 'Pole'
        else:
            l_attributes = self.stimulusAttributes[p_type]
            l_rootName = 'Bodziec (typ: ' + p_type + ')'
            
        l_root = UGMPropertiesRoot(l_rootName, p_type)
        p_property = UGMProperty('id', 0, 'int', {})
        for i_attributeName in l_attributes:
            p_property = UGMProperty(i_attributeName, 
                                     self.attributeTypes[i_attributeName]['default'], 
                                     self.attributeTypes[i_attributeName]['type'], 
                                     self.attributeTypes[i_attributeName]['parameters'])
            l_root.addChild(p_property)
        p_stimulusesRoot = UGMPropertiesRoot('stimuluses', 'list')
        l_root.addChild(p_stimulusesRoot)
        l_root.setupDependents()
        return l_root
        
    def removeRoot(self, p_parentIndex, p_position):
        """Removes child of given parent at given position from model"""
        self.structureModified = True
        l_parentItem = self.getItem(p_parentIndex)

        self.beginRemoveRows(p_parentIndex, p_position, p_position)
        l_parentItem.removeChild(p_position)
        self.endRemoveRows()
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        """Returns number of rows for given parent item"""
        parentItem = self.getItem(parent)
        return parentItem.childCount()
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        """Returns number of columns"""
        return 2
    
    def flags(self, index):
        """Returns flags for given index in properties list: whether this item is
        enabled, editable, selectable, etc."""
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        else:
            item = self.getItem(index)
            if item.editable(index.column()):
                return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            else:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Returns data/value of given index, for given role"""
        if not index.isValid():
            return None
        
        column = index.column()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if column == NAME:
                return self.getItem(index).data(NAME)
            elif column == VALUE:
                return self.getItem(index).data(VALUE)
        
        return None
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """Sets data for given index if possible"""
        if role != QtCore.Qt.EditRole:
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
        """Returns parent item for given index"""
        if not index.isValid():
            return QtCore.QModelIndex()
        
        childItem = self.getItem(index)
        parentItem = childItem.parent()
        
        if parentItem == self.rootItem:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentItem.childNumber(), 0, parentItem)
    
    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Returns or creates QModelIndex for given row/column and parent"""
        if (not self.hasIndex(row, column, parent)) or (parent.isValid() and parent.column() != 0):
            return QtCore.QModelIndex()
        
        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()
    
    def getItem(self, index):
        """Returns item, that is pointed by given QModelIndex."""
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        
        return self.rootItem
