from PyQt4 import QtCore, QtGui
from time import sleep
import sys, os

class MyCustomWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,1)
        layout.addWidget(self.progressBar)
        button = QtGui.QPushButton("Start", self)
        layout.addWidget(button)      

        button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)

    def onStart(self): 
        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0,1)
        self.progressBar.setValue(1)


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        os.system('sudo apt-get install leafpad')
        self.taskFinished.emit() 

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyCustomWidget()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
