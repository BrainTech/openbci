# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'obci_launcher.ui'
#
# Created: Thu Feb 16 11:30:38 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.6
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ObciLauncher(object):
    def setupUi(self, ObciLauncher):
        ObciLauncher.setObjectName("ObciLauncher")
        ObciLauncher.resize(761, 455)
        self.gridLayout = QtGui.QGridLayout(ObciLauncher)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(ObciLauncher)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtGui.QGroupBox(self.splitter)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scenarios = QtGui.QTableWidget(self.groupBox)
        self.scenarios.setColumnCount(3)
        self.scenarios.setObjectName("scenarios")
        self.scenarios.setColumnCount(3)
        self.scenarios.setRowCount(0)
        self.scenarios.horizontalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.scenarios)
        self.groupBox_3 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.info = QtGui.QLabel(self.groupBox_3)
        self.info.setWordWrap(True)
        self.info.setOpenExternalLinks(True)
        self.info.setObjectName("info")
        self.gridLayout_2.addWidget(self.info, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.start_button = QtGui.QPushButton(self.groupBox)
        self.start_button.setObjectName("start_button")
        self.horizontalLayout.addWidget(self.start_button)
        self.stop_button = QtGui.QPushButton(self.groupBox)
        self.stop_button.setObjectName("stop_button")
        self.horizontalLayout.addWidget(self.stop_button)
        self.reset_button = QtGui.QPushButton(self.groupBox)
        self.reset_button.setObjectName("reset_button")
        self.horizontalLayout.addWidget(self.reset_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.parameters_of = QtGui.QGroupBox(self.splitter)
        self.parameters_of.setObjectName("parameters_of")
        self.gridLayout_3 = QtGui.QGridLayout(self.parameters_of)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.parameters = QtGui.QTreeWidget(self.parameters_of)
        self.parameters.setObjectName("parameters")
        self.parameters.headerItem().setText(0, "1")
        self.gridLayout_3.addWidget(self.parameters, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(ObciLauncher)
        QtCore.QMetaObject.connectSlotsByName(ObciLauncher)

    def retranslateUi(self, ObciLauncher):
        ObciLauncher.setWindowTitle(QtGui.QApplication.translate("ObciLauncher", "Obci Launcher", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ObciLauncher", "Experiment scenarios", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("ObciLauncher", "Information", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setText(QtGui.QApplication.translate("ObciLauncher", "asjdn asjklndjk naskljdh jkashdjk ashdkjhas kjashd akljshdk jlasd kjahdkjashd kjahsdjk hasdjlhasdklj hadkljashd lashd kjash djkashdkj ahsd lash", None, QtGui.QApplication.UnicodeUTF8))
        self.start_button.setText(QtGui.QApplication.translate("ObciLauncher", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.stop_button.setText(QtGui.QApplication.translate("ObciLauncher", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_button.setText(QtGui.QApplication.translate("ObciLauncher", "Hard Reset", None, QtGui.QApplication.UnicodeUTF8))
        self.parameters_of.setTitle(QtGui.QApplication.translate("ObciLauncher", "Parameters", None, QtGui.QApplication.UnicodeUTF8))

