# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ParamsDialog.ui'
#
# Created: Mon Feb 06 19:54:17 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class CspParamsDialog(object):
    def setupUi(self, SetParameters):
        SetParameters.setObjectName(_fromUtf8("SetParameters"))
        SetParameters.resize(410, 154)
        self.verticalLayout = QtGui.QVBoxLayout(SetParameters)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.bufferTimeLabel = QtGui.QLabel(SetParameters)
        self.bufferTimeLabel.setObjectName(_fromUtf8("bufferTimeLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.bufferTimeLabel)
        self.buf_time = QtGui.QDoubleSpinBox(SetParameters)
        self.buf_time.setDecimals(5)
        self.buf_time.setMaximum(10.0)
        self.buf_time.setSingleStep(0.5)
        self.buf_time.setObjectName(_fromUtf8("buf_time"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.buf_time)
        self.verticalLayout.addLayout(self.formLayout)
        self.groupBox = QtGui.QGroupBox(SetParameters)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.f0 = QtGui.QSpinBox(self.groupBox)
        self.f0.setMinimum(1)
        self.f0.setMaximum(100)
        self.f0.setSingleStep(1)
        self.f0.setObjectName(_fromUtf8("f0"))
        self.gridLayout_2.addWidget(self.f0, 0, 0, 1, 1)
        self.f1 = QtGui.QSpinBox(self.groupBox)
        self.f1.setMinimum(1)
        self.f1.setObjectName(_fromUtf8("f1"))
        self.gridLayout_2.addWidget(self.f1, 0, 1, 1, 1)
        self.f2 = QtGui.QSpinBox(self.groupBox)
        self.f2.setMinimum(1)
        self.f2.setObjectName(_fromUtf8("f2"))
        self.gridLayout_2.addWidget(self.f2, 0, 2, 1, 1)
        self.f3 = QtGui.QSpinBox(self.groupBox)
        self.f3.setMinimum(1)
        self.f3.setObjectName(_fromUtf8("f3"))
        self.gridLayout_2.addWidget(self.f3, 0, 3, 1, 1)
        self.f4 = QtGui.QSpinBox(self.groupBox)
        self.f4.setMinimum(1)
        self.f4.setObjectName(_fromUtf8("f4"))
        self.gridLayout_2.addWidget(self.f4, 1, 0, 1, 1)
        self.f5 = QtGui.QSpinBox(self.groupBox)
        self.f5.setMinimum(1)
        self.f5.setObjectName(_fromUtf8("f5"))
        self.gridLayout_2.addWidget(self.f5, 1, 1, 1, 1)
        self.f6 = QtGui.QSpinBox(self.groupBox)
        self.f6.setMinimum(1)
        self.f6.setObjectName(_fromUtf8("f6"))
        self.gridLayout_2.addWidget(self.f6, 1, 2, 1, 1)
        self.f7 = QtGui.QSpinBox(self.groupBox)
        self.f7.setMinimum(1)
        self.f7.setObjectName(_fromUtf8("f7"))
        self.gridLayout_2.addWidget(self.f7, 1, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(SetParameters)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SetParameters)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SetParameters.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SetParameters.reject)
        QtCore.QMetaObject.connectSlotsByName(SetParameters)

    def retranslateUi(self, SetParameters):
        SetParameters.setWindowTitle(QtGui.QApplication.translate("SetParameters", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.bufferTimeLabel.setText(QtGui.QApplication.translate("SetParameters", "Buffer Time [s]", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SetParameters", "Frequencies", None, QtGui.QApplication.UnicodeUTF8))
        self.f0.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 0", None, QtGui.QApplication.UnicodeUTF8))
        self.f1.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 1", None, QtGui.QApplication.UnicodeUTF8))
        self.f2.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 2", None, QtGui.QApplication.UnicodeUTF8))
        self.f3.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 3", None, QtGui.QApplication.UnicodeUTF8))
        self.f4.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 4", None, QtGui.QApplication.UnicodeUTF8))
        self.f5.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 5", None, QtGui.QApplication.UnicodeUTF8))
        self.f6.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 6", None, QtGui.QApplication.UnicodeUTF8))
        self.f7.setToolTip(QtGui.QApplication.translate("SetParameters", "Field 7", None, QtGui.QApplication.UnicodeUTF8))

