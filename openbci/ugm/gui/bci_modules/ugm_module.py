# -*- coding: utf-8 -*-

import sip
sip.setapi('QVariant', 2)

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import bci_plugin
from gui.UGMMain import Ui_UGMMainWidget
from ugm.data import UGM_data
from ugm.attributes import UGM_attributes_def, UGM_attributes_for_elem

class ugm_module_plugin(bci_plugin.BciBasePlugin):
	
	name = u"UGM"
	
	def __init__(self):
		self.dockWidget = None
	
	def buildGui(self, p_parent):
		if self.dockWidget == None:
			self.dockWidget = UGMModuleDockWidget(p_parent)
		return self.dockWidget

class UGMModuleDockWidget(QDockWidget):
	def __init__(self, parent=None):
		QDockWidget.__init__(self, parent)
		self.ui = Ui_UGMMainWidget()
		self.ui.setupUi(self)
		self.propertiesModel = UGMPropertiesModel(UGM_attributes_def, UGM_attributes_for_elem, UGM_data)
		self.delegate = UGMPropertiesDelegate()
		self.ui.propertyList.setModel(self.propertiesModel)
		self.ui.propertyList.setItemDelegate(self.delegate)
		self.ui.propertyList.setEditTriggers(QAbstractItemView.AllEditTriggers)
		self.resizeColumns()
		self.connect(self.ui.propertyList, SIGNAL("collapsed(QModelIndex)"), self.resizeColumns)
		self.connect(self.ui.propertyList, SIGNAL("expanded(QModelIndex)"), self.resizeColumns)
	
	def resizeColumns(self, p_index=None):
		for i_column in range(self.propertiesModel.columnCount(QModelIndex())):
			self.ui.propertyList.resizeColumnToContents(i_column)

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


class UGMPropertiesRoot(UGMTreeElement):
	def __init__(self, p_name, p_children=[], p_parent=None):
		self.name = p_name
		self.children = {}
		self.childItems = []
		self.type = 'root'
		for i_child in p_children:
			self.addChild(i_child)
		self.parentItem = p_parent
			
	def addChild(self, p_child):
		self.childItems.append(p_child)
		self.children[p_child.name] = p_child
		p_child.setParent(self)
	
	def setupDependents(self):
		for i_child in self.childItems:
			if i_child.type == 'dependent':
				l_depends_on = self.children[i_child.dependentParameters['depends_on']]
				l_depends_on.addDependingItem(i_child)
				i_child.dependedItemChanged(l_depends_on.value, False)		
		
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
		return False # TODO: Edycja nazwy?
	
	def editable(self, column):
		return False


class UGMPropertiesModel(QAbstractItemModel):
	
	def __init__(self, p_attributes, p_attributesForElements, p_data, parent=None):
		super(UGMPropertiesModel, self).__init__(parent)
		self.loadAttributeTypes(p_attributes)
		self.setAttributeSubtypes()
		self.setAttributesForElements(p_attributesForElements)
		self.rootItem = self.createRoot(p_data, 'fields', 'Root')
		# TODO: setFirstColumnSpanned na rootach
	
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
						'subtypes': l_value}
					}
			else:
				# Enumerated type
				l_attributeType = \
					{'type': 'enumerated',
					'parameters':
						{'values': l_value}
					}
		else:
			# Simple type
			l_attributeType = {'type': l_value, 'parameters': None}
		
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
		l_root = UGMPropertiesRoot(p_name)
		for i_subitem in p_subitems:
			p_subItemsRoot = self.createFieldsRoot(i_subitem, p_subitems_type)
			l_root.addChild(p_subItemsRoot)
		l_root.setupDependents()
		return l_root
	
	def createFieldsRoot(self, p_field, p_subitems_type):
		if (p_subitems_type == 'fields'):
			l_rootName = 'Pole (id: ' + str(p_field['id']) + ')'
			l_attributes = self.fieldAttributes
		else: # p_subitems_type == 'stimuluses'
			l_stimulusType = p_field['stimulus_type']
			l_rootName = 'Bodziec (id: ' + str(p_field['id']) + ', typ: ' + l_stimulusType + ')'
			l_attributes = self.stimulusAttributes[l_stimulusType]
		
		l_root = UGMPropertiesRoot(l_rootName)
		for i_attributeName in l_attributes:
			p_property = UGMProperty(i_attributeName, p_field[i_attributeName], self.attributeTypes[i_attributeName]['type'], self.attributeTypes[i_attributeName]['parameters'])
			l_root.addChild(p_property)
		if 'stimuluses' in p_field:
			p_stimulusesRoot = self.createRoot(p_field['stimuluses'], 'stimuluses', u'Bodźce')
			l_root.addChild(p_stimulusesRoot)
		l_root.setupDependents()
		return l_root
	
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
	


class UGMPropertiesDelegate(QItemDelegate):
	def createEditor(self, parent, option, index):
		l_item = self.getItem(index)
		l_type = l_item.type
		l_typeParameters = l_item.typeParameters
		
		if l_type == 'int':
			editor = QSpinBox(parent)
			editor.setSingleStep(1)
			editor.setMaximum(1000)
		elif l_type == 'float':
			editor = QDoubleSpinBox(parent)
			editor.setSingleStep(0.05)
			editor.setMaximum(1000)			
		elif l_type == 'string':
			editor = QLineEdit(parent)
		elif l_type == 'enumerated':
			editor = QComboBox(parent)
			for i_value in l_typeParameters['values']:
				editor.addItem(i_value)
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
	
