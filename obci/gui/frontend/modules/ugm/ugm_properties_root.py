# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#      Łukasz Polak <l.polak@gmail.com>
#
"""Tree element, that represents root in properties tree"""

from obci.gui.frontend.modules.ugm.ugm_tree_element import UGMTreeElement, NAME

class UGMPropertiesRoot(UGMTreeElement):
    """Tree element, that represents root in properties tree"""
    def __init__(self, p_name, p_type, p_children=[], p_parent=None):
        super(UGMPropertiesRoot, self).__init__()
        self.name = p_name
        self.children = {}
        self.childItems = []
        self.type = p_type
        for i_child in p_children:
            self.addChild(i_child)
        self.parentItem = p_parent
    
    def addChild(self, p_child):
        """Add single child to this root"""
        self.childItems.append(p_child)
        if self.type != 'list':
            self.children[p_child.name] = p_child
        p_child.setParent(self)
        
    def removeChild(self, p_position):
        """Remove single child from given position on children list"""
        if self.type != 'list':
            del self.children[self.childItems[p_position].name]
        del self.childItems[p_position]
    
    def setupDependents(self):
        """Check childrens dependents, and set them if needed"""
        for i_child in self.childItems:
            if i_child.type == 'dependent':
                l_depends_on = self.children[i_child.dependentParameters['depends_on']]
                l_depends_on.addDependingItem(i_child)
                i_child.dependedItemChanged(l_depends_on.value, False)      
    
    def createConfigNode(self):
        """Prepare single node of configuration file, that is represented by 
        this root"""
        if self.type != 'list':
            l_node = {}
            # To create config node of ours, we must create one for each child
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
        """Return child of this root, at given row"""
        return self.childItems[row]
    
    def childCount(self):
        """Return number of children this root has"""
        return len(self.childItems)
    
    def columnCount(self):
        """Roots have one column, so we return 1 :)"""
        return 1
    
    def data(self, column):
        """Return name of this root"""
        if column == NAME:
            return self.name
    
    def setData(self, column, value):
        """Cannot set data for roots"""
        return False
    
    def editable(self, column):
        """Roots are non-editable, so returns false"""
        return False
