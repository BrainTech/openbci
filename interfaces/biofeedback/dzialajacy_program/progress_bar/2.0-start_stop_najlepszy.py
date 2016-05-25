import sys, time
from PyQt4 import QtGui, QtCore

class ProgressBar(QtGui.QWidget):
    def __init__(self, parent=None, total=20):
        super(ProgressBar, self).__init__(parent)
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setMinimum(1)
        self.progressbar.setMaximum(total)
        self.button = QtGui.QPushButton('Start')
        self.button.clicked.connect(self.handleButton)
        main_layout = QtGui.QGridLayout()
        main_layout.addWidget(self.button, 0, 0)
        main_layout.addWidget(self.progressbar, 0, 1)
        self.setLayout(main_layout)
        self.setWindowTitle('Progress')
        self._active = False

    def handleButton(self):
        if not self._active:
            self._active = True
            self.button.setText('Stop')
            if self.progressbar.value() == self.progressbar.maximum():
                self.progressbar.reset()
            QtCore.QTimer.singleShot(0, self.startLoop)
        else:
            self._active = False

    def closeEvent(self, event):
        self._active = False

    def startLoop(self):
        while True:
            time.sleep(0.05)
            value = self.progressbar.value() + 1
            self.progressbar.setValue(value)
            QtGui.qApp.processEvents()
            if (not self._active or
                value >= self.progressbar.maximum()):
                break
        self.button.setText('Start')
        self._active = False

app = QtGui.QApplication(sys.argv)
bar = ProgressBar(total=101)
bar.show()
sys.exit(app.exec_())
