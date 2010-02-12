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
"""Tree element, that represents root in properties tree"""

from modules.ugm.gui.ugm_tree_element import UGMTreeElement, NAME

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