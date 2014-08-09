# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'select_amplifier_dialog.ui'
#
# Created: Sat Aug  9 00:12:32 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SelectAmplifier(object):
    def setupUi(self, SelectAmplifier):
        SelectAmplifier.setObjectName(_fromUtf8("SelectAmplifier"))
        SelectAmplifier.resize(400, 300)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SelectAmplifier)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(SelectAmplifier)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.refreshButton = QtGui.QPushButton(self.groupBox)
        self.refreshButton.setObjectName(_fromUtf8("refreshButton"))
        self.verticalLayout.addWidget(self.refreshButton)
        self.amplifiers = QtGui.QTableWidget(self.groupBox)
        self.amplifiers.setObjectName(_fromUtf8("amplifiers"))
        self.amplifiers.setColumnCount(0)
        self.amplifiers.setRowCount(0)
        self.verticalLayout.addWidget(self.amplifiers)
        self.buttonBox = QtGui.QDialogButtonBox(self.groupBox)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(SelectAmplifier)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SelectAmplifier.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SelectAmplifier.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectAmplifier)

    def retranslateUi(self, SelectAmplifier):
        SelectAmplifier.setWindowTitle(_translate("SelectAmplifier", "Connect to machine", None))
        self.groupBox.setTitle(_translate("SelectAmplifier", "Amplifiers", None))
        self.refreshButton.setText(_translate("SelectAmplifier", "Refresh", None))

