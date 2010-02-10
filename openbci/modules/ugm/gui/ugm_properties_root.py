# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from modules.ugm.gui.ugm_tree_element import UGMTreeElement, NAME, VALUE

class UGMPropertiesRoot(UGMTreeElement):
    def __init__(self, p_name, p_type, p_children=[], p_parent=None):
        self.name = p_name
        self.children = {}
        self.childItems = []
        self.type = p_type
        for i_child in p_children:
            self.addChild(i_child)
        self.parentItem = p_parent
    
    def addChild(self, p_child):
        self.childItems.append(p_child)
        if self.type != 'list':
            self.children[p_child.name] = p_child
        p_child.setParent(self)
        
    def removeChild(self, p_position):
        if self.type != 'list':
            del self.children[self.childItems[p_position].name]
        del self.childItems[p_position]
    
    def setupDependents(self):
        for i_child in self.childItems:
            if i_child.type == 'dependent':
                l_depends_on = self.children[i_child.dependentParameters['depends_on']]
                l_depends_on.addDependingItem(i_child)
                i_child.dependedItemChanged(l_depends_on.value, False)      
    
    def createConfigNode(self):
        if self.type != 'list':
            l_node = {}
            for i_child in self.childItems:
                l_node[i_child.name] = i_child.createConfigNode()
            if self.type != 'field': # this is stimulus
                l_node['stimulus_type'] = self.type
        else:
            l_node = []
            for i_child in self.childItems:
                l_node.append(i_child.createConfigNode())
                
        return l_node
    
    def child(self, row):
        return self.childItems[row]
    
    def childCount(self):
        return len(self.childItems)
    
    def columnCount(self):
        return 1
    
    def data(self, column):
        if column == NAME:
            return self.name
    
    def setData(self, column, value):
        return False
    
    def editable(self, column):
        return False