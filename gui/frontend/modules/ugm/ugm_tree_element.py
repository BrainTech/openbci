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
"""UGM properties tree element, that represents single element in model, should
be subclassed"""

from PyQt4 import QtCore
NAME, VALUE = range(2)

class UGMTreeElement(object):
    """UGM properties tree element, that represents single element in model, should
    be subclassed"""
    def __init__(self):
        self.parentItem = None
    
    def childNumber(self):
        """Returns position of this item on list of children of its parent"""
        if self.parentItem != None:
            return self.parentItem.childItems.index(self)
        return 0
    
    def parent(self):
        """Return parent of this item"""
        return self.parentItem
    
    def setParent(self, parent):
        """Sets parent of this item"""
        self.parentItem = parent
    
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Returns headers names for tree"""
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ['Nazwa', u'Wartość']
        
        return None