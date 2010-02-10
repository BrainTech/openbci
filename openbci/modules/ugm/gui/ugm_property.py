# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from modules.ugm.gui.ugm_tree_element import UGMTreeElement, NAME, VALUE

class UGMProperty(UGMTreeElement):
    def __init__(self, p_name, p_value, p_type, p_typeParameters=None, p_parent=None):
        self.name = p_name
        self.value = p_value
        self.type = p_type
        if (self.type == 'dependent'):
            self.dependentParameters = p_typeParameters
        else:
            self.typeParameters = p_typeParameters          
        self.parentItem = p_parent
        self.dependingItems = []
    
    def addDependingItem(self, p_item):
        self.dependingItems.append(p_item)
    
    def dependedItemChanged(self, p_value, p_modify_value=True):
        l_newType = self.dependentParameters['subtypes'][p_value]
        if l_newType['type'] != self.type:
            self.type = l_newType['type']
            self.typeParameters = l_newType['parameters']
            if p_modify_value:
                if self.type == 'int':
                    self.value = 0
                elif self.type == 'string':
                    self.value = ''
                elif self.type == 'enumerated':
                    self.value = self.typeParameters['values'][0]
                else:
                    self.value = None
    
    def hasDependents(self):
        if not self.dependingItems:
            return False
        else:
            return True
    
    def createConfigNode(self):
        return self.value
    
    def childCount(self):
        return 0
    
    def columnCount(self):
        return 2
    
    def data(self, column):
        if column == NAME:
            return self.name
        elif column == VALUE:
            return self.value
    
    def setData(self, column, value):
        if column == VALUE and self.value != value:
            self.value = value
            for i_dependingItem in self.dependingItems:
                i_dependingItem.dependedItemChanged(value)
            return True
        else:
            return False
    
    def editable(self, column):
        if column == VALUE:
            return True
        else:
            return False