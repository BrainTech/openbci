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
"""UGM properties tree element, that represents single property of some field or
stimulues in model"""

from modules.ugm.gui.ugm_tree_element import UGMTreeElement, NAME, VALUE

class UGMProperty(UGMTreeElement):
    """UGM properties tree element, that represents single property of some field or
    stimulues in model"""
    def __init__(self, p_name, p_value, p_type, p_typeParameters=None, p_parent=None):
        super(UGMProperty, self).__init__()
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
        """Adds given item as being dependent of this property"""
        self.dependingItems.append(p_item)
    
    def dependedItemChanged(self, p_value, p_modify_value=True):
        """Called, when item on which this property depends is changed"""
        l_newType = self.dependentParameters['subtypes'][p_value]
        if l_newType['type'] != self.type:
            # Type changed! Our values type possibly could change too :)
            self.type = l_newType['type']
            self.typeParameters = l_newType['parameters']
            if self.value == None or p_modify_value:
                self.setDefaultValue()
                    
    def setDefaultValue(self):
        if self.type == 'int':
            self.value = 0
        elif self.type == 'float':
            self.value = 0
        elif self.type == 'string':
            self.value = ''
        elif self.type == 'color':
            self.value = '#000000'
        elif self.type == 'font':
            self.value = 'serif'
        elif self.type == 'enumerated':
            self.value = self.typeParameters['values'][0]
        else:
            self.value = None
    
    def hasDependents(self):
        """Returns true if any property depends on this one"""
        if not self.dependingItems:
            return False
        else:
            return True
    
    def createConfigNode(self):
        """Returns config node representing this property in configuration 
        dictionary"""
        return self.value
    
    def childCount(self):
        """Returns 0, because property doesn't have children :)"""
        return 0
    
    def columnCount(self):
        """Returns 2, because properties has name and value columns"""
        return 2
    
    def data(self, column):
        """Returns data for given column (name or value)"""
        if column == NAME:
            return self.name
        elif column == VALUE:
            return self.value
    
    def setData(self, column, value):
        """Sets value of property"""
        if column == VALUE and self.value != value:
            self.value = value
            for i_dependingItem in self.dependingItems:
                i_dependingItem.dependedItemChanged(value)
            return True
        else:
            return False
    
    def editable(self, column):
        """Returns true for value column, false otherwise"""
        if column == VALUE:
            return True
        else:
            return False