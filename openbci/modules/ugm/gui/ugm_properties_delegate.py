# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class UGMPropertiesDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        l_item = self.getItem(index)
        l_type = l_item.type
        l_typeParameters = l_item.typeParameters
        
        if l_type == 'int':
            editor = QSpinBox(parent)
            editor.setSingleStep(1)
            editor.setMaximum(1000)
            self.connect(editor, SIGNAL('valueChanged(int)'), self.editorValueChanged)
        elif l_type == 'float':
            editor = QDoubleSpinBox(parent)
            editor.setSingleStep(0.05)
            editor.setMaximum(1000)   
            self.connect(editor, SIGNAL('valueChanged(double)'), self.editorValueChanged)
        elif l_type == 'string':
            editor = QLineEdit(parent)
            self.connect(editor, SIGNAL('textChanged(QString)'), self.editorValueChanged)
        elif l_type == 'enumerated':
            editor = QComboBox(parent)
            for i_value in l_typeParameters['values']:
                editor.addItem(i_value)
            self.connect(editor, SIGNAL('currentIndexChanged(int)'), self.editorValueChanged)
        else:
            editor = None
        
        return editor
    
    def setEditorData(self, editor, index):
        l_value = index.model().data(index, Qt.EditRole)
        l_item = self.getItem(index)
        l_type = l_item.type
        l_typeParameters = l_item.typeParameters
        
        if l_type == 'int' or l_type == 'float':
            editor.setValue(l_value)
        elif l_type == 'string':
            editor.setText(QString(str(l_value)))
        elif l_type == 'enumerated':
            editor.setCurrentIndex(editor.findText(l_value))
    
    def setModelData(self, p_editor, model, index):
        l_item = self.getItem(index)
        l_type = l_item.type
        l_type_parameters = l_item.typeParameters
        
        if l_type == 'int' or l_type == 'float':
            p_editor.interpretText()
            l_value = p_editor.value()
        elif l_type == 'string':
            l_value = str(p_editor.text())
        elif l_type == 'enumerated':
            l_value = str(p_editor.currentText())
        else:
            return
        
        model.setData(index, l_value, Qt.EditRole)
    
    def editorValueChanged(self):
        self.emit(SIGNAL('commitData(QWidget *)'), self.sender())
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def getItem(self, index):
        """
        Returns item, that is pointed by given QModelIndex.
        """
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        
        return self.rootItem
