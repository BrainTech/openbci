# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

NAME, VALUE = range(2)

class UGMTreeElement(object):
    def childNumber(self):
        if self.parentItem != None:
            return self.parentItem.childItems.index(self)
        return 0
    
    def parent(self):
        return self.parentItem
    
    def setParent(self, parent):
        self.parentItem = parent
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ['Nazwa', u'Wartość']
        
        return None