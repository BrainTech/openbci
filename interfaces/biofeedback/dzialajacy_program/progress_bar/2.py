import sys, time
from PyQt4 import QtGui, QtCore

class MyCustomWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)       

        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,100)
        #button = QtGui.QPushButton("Start", self)
        layout.addWidget(self.progressBar)
        #layout.addWidget(button)

        #button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.notifyProgress.connect(self.onProgress)


    def onStart(self):
        self.myLongTask.start()

    def onProgress(self, i):
        self.progressBar.setValue(i)


class TaskThread(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def run(self):
        for i in range(101):
            self.notifyProgress.emit(i)
            time.sleep(0.01)


app = QtGui.QApplication(sys.argv)
bar = MyCustomWidget()
bar.show()
sys.exit(app.exec_())
