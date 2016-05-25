from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
import sys

class myProgressBar(QtGui.QProgressBar):
  value = 0  
    
  @pyqtSlot()
  def increaseValue(self):
    
    self.setValue(self.value)
    self.value = self.value+1


def main():    
    app 	 = QtGui.QApplication(sys.argv)
    progressBar	 = myProgressBar()

    #Resize width and height
    progressBar.resize(250,50)    
    progressBar.setWindowTitle('PyQt QProgressBar Set Value Example')  
    
    timer = QtCore.QTimer()
    progressBar.connect(timer,SIGNAL("timeout()"),progressBar,SLOT("increaseValue()"))
    timer.start(1000) 

    progressBar.show()    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
