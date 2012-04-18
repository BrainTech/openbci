# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connect_dialog.ui'
#
# Created: Mon Apr 16 16:03:02 2012
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConnectToMachine(object):
    def setupUi(self, ConnectToMachine):
        ConnectToMachine.setObjectName(_fromUtf8("ConnectToMachine"))
        ConnectToMachine.resize(400, 300)
        ConnectToMachine.setWindowTitle(QtGui.QApplication.translate("ConnectToMachine", "Connect to machine", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout_2 = QtGui.QVBoxLayout(ConnectToMachine)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(ConnectToMachine)
        self.groupBox.setTitle(QtGui.QApplication.translate("ConnectToMachine", "Nearby machines", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.nearby_machines = QtGui.QTableWidget(self.groupBox)
        self.nearby_machines.setObjectName(_fromUtf8("nearby_machines"))
        self.nearby_machines.setColumnCount(0)
        self.nearby_machines.setRowCount(0)
        self.verticalLayout.addWidget(self.nearby_machines)
        self.buttonBox = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(ConnectToMachine)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConnectToMachine.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConnectToMachine.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectToMachine)

    def retranslateUi(self, ConnectToMachine):
        pass

