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
        self._ruchy = []  #nowe
        self._count = 0
        self._active = False
    
    def handleButton(self):
        if not self._active:
            self._active = True
            self._ruchy.append(1)
            self.button.setText('Stop')
            if self.progressbar.value() == self.progressbar.maximum():
                self.progressbar.reset()
            QtCore.QTimer.singleShot(0, self.startLoop)
        else:
            self._active = False
			
    def closeEvent(self, event):
        self._active = False

    def nextProcent(self):
        """ switch to next image or previous image
        """
        if self._imagesInList:

            if self.animFlag:
                self._count += 1
            else:
                self._count -= 1

            if self._count in range(100): #ruch procentow przod lub tyl 
				for x in xrange(10):
					continue
					#self.progressbar.value() = self.progressbar.value() - 1
                
            else: #napis super! udalo ci sie osiagnac cel
                self.close()


    def startLoop(self):
        while True:
            time.sleep(0.05)
            K = [11,21,31,41,51,61,71,81,91]
            value = self.progressbar.value() + 1
            self.progressbar.setValue(value)
            QtGui.qApp.processEvents()
            print self._count #nowe
         #   print raw_input('Podaj wartosc:')
            if (not self._active or
                value >= self.progressbar.maximum()
                or self.progressbar.value() in K):
                break
        self.button.setText('Start')
        self._active = False

app = QtGui.QApplication(sys.argv)
bar = ProgressBar(total=101)
bar.show()
sys.exit(app.exec_())
