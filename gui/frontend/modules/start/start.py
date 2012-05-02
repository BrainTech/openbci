# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'start.ui'
#
# Created: Tue Oct 12 02:47:48 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(460, 402)
        self.Amplifier = QtGui.QPushButton(Form)
        self.Amplifier.setGeometry(QtCore.QRect(20, 130, 141, 27))
        self.Amplifier.setObjectName("Amplifier")
        self.Experiment = QtGui.QPushButton(Form)
        self.Experiment.setGeometry(QtCore.QRect(20, 170, 141, 27))
        self.Experiment.setObjectName("Experiment")
        self.Pokaz = QtGui.QPushButton(Form)
        self.Pokaz.setGeometry(QtCore.QRect(20, 210, 141, 27))
        self.Pokaz.setObjectName("Pokaz")
        self.AddMonitor = QtGui.QPushButton(Form)
        self.AddMonitor.setGeometry(QtCore.QRect(190, 130, 111, 27))
        self.AddMonitor.setObjectName("AddMonitor")
        self.AddSpectrum = QtGui.QPushButton(Form)
        self.AddSpectrum.setGeometry(QtCore.QRect(190, 170, 111, 27))
        self.AddSpectrum.setObjectName("AddSpectrum")
        self.AddExperiment = QtGui.QPushButton(Form)
        self.AddExperiment.setGeometry(QtCore.QRect(190, 210, 111, 27))
        self.AddExperiment.setObjectName("AddExperiment")
        self.textBrowser = QtGui.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 161, 91))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser_2 = QtGui.QTextBrowser(Form)
        self.textBrowser_2.setGeometry(QtCore.QRect(190, 10, 231, 101))
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.Demo = QtGui.QPushButton(Form)
        self.Demo.setGeometry(QtCore.QRect(20, 290, 93, 27))
        self.Demo.setObjectName("Demo")
        self.Stop = QtGui.QPushButton(Form)
        self.Stop.setGeometry(QtCore.QRect(140, 370, 93, 27))
        self.Stop.setObjectName("Stop")
        self.VirtualAmplifier = QtGui.QPushButton(Form)
        self.VirtualAmplifier.setGeometry(QtCore.QRect(20, 250, 141, 27))
        self.VirtualAmplifier.setObjectName("VirtualAmplifier")
        self.textBrowser_3 = QtGui.QTextBrowser(Form)
        self.textBrowser_3.setGeometry(QtCore.QRect(120, 290, 141, 71))
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(310, 140, 81, 17))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(310, 180, 81, 17))
        self.label_2.setObjectName("label_2")
        self.monitorChannel = QtGui.QTextEdit(Form)
        self.monitorChannel.setGeometry(QtCore.QRect(390, 130, 31, 31))
        self.monitorChannel.setObjectName("monitorChannel")
        self.spectrumChannel = QtGui.QTextEdit(Form)
        self.spectrumChannel.setGeometry(QtCore.QRect(390, 170, 31, 31))
        self.spectrumChannel.setObjectName("spectrumChannel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.Amplifier.setText(QtGui.QApplication.translate("Form", "Start Amplifier", None, QtGui.QApplication.UnicodeUTF8))
        self.Experiment.setText(QtGui.QApplication.translate("Form", "Start Experiment", None, QtGui.QApplication.UnicodeUTF8))
        self.Pokaz.setText(QtGui.QApplication.translate("Form", "Start Pokaz", None, QtGui.QApplication.UnicodeUTF8))
        self.AddMonitor.setText(QtGui.QApplication.translate("Form", "Add Monitor", None, QtGui.QApplication.UnicodeUTF8))
        self.AddSpectrum.setText(QtGui.QApplication.translate("Form", "Add Spectrum", None, QtGui.QApplication.UnicodeUTF8))
        self.AddExperiment.setText(QtGui.QApplication.translate("Form", "Add Experiment", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose one of these components first:...</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser_2.setHtml(QtGui.QApplication.translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">... and if you need sth more add as many components of these as you wish:</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.Demo.setText(QtGui.QApplication.translate("Form", "Demo", None, QtGui.QApplication.UnicodeUTF8))
        self.Stop.setText(QtGui.QApplication.translate("Form", "STOP", None, QtGui.QApplication.UnicodeUTF8))
        self.VirtualAmplifier.setText(QtGui.QApplication.translate("Form", "Virtual Amplifier", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser_3.setHtml(QtGui.QApplication.translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">... and press STOP to finish:</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "of channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "of channel", None, QtGui.QApplication.UnicodeUTF8))

