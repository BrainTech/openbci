#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ServerController(QObject):

    # all values in miliseconds
    serverPingDelay    = 1000
    serverPingTimeout  = 100
    serverReadyTimeout = 10*serverPingDelay
    
    serverShutdownTimeout = 1000#10*1000

    serverReady           = pyqtSignal()          # emited when server is fully operational
    serverStartingUpError = pyqtSignal('QString') # emited when error was detected during startup
    
    serverTerminated        = pyqtSignal()          # emited when server process ends by request
    serverShuttingDownError = pyqtSignal('QString') # emited when error occurred during shutting down
    
    serverUnexpectedlyDied = pyqtSignal('QString') # emited when server unexpectedly died during running

    def __init__(self, parent=None):
        super(ServerController, self).__init__(parent)
        
        self.process = QProcess()
        self.programName = 'obci srv'
        
        self.process.started.connect(self.startPinging)
        self.process.error.connect(self.processError)
        #self.process.finished.connect(self.processFinished)
        
        self.pingingStartTime = QTime()
        self.startingServer = False
        
        self.terminatingServer = False

        self.startServer()

    #---------------------------------------------------------------------------

    def isServerRunning(self):
        print("isServerRunning? ", self.process.state())
        return True#self.process.state() == QProcess.Running
    
    def isServerResponding(self):
        # TODO: !!!!!!!!!
        return self.isServerRunning()
        
    def startServer(self):
        if 1 == 1:#not self.isServerRunning():
            self.startingServer = True
            self.process.start(self.programName)
    
    def stopServer(self):
        if self.isServerRunning():
            print("stopServer.isRunning")
            self.terminatingServer = True
            os.system('obci srv_kill')
            self.process.terminate()
            QTimer.singleShot(self.serverShutdownTimeout, self.checkShutdownTimeout)
        else:
            print("stopServer.isNotRunning...")
        
    #---------------------------------------------------------------------------
    
    def startPinging(self):
        self.pingingStartTime = QTime.currentTime()
        QTimer.singleShot(self.serverPingDelay, self.pingServer)
        
    def pingServer(self):
        print("Ping obci server")
        if not self.startingServer:
            print("pingServer.Not starting")
            return
    
        if self.process.state() != QProcess.Running:
            print("pingServer.Not running")
            self.startingServer = False
            self.serverStartingUpError.emit(self.tr('Server suddenly died...'))           
            return
        
        if self.isServerResponding():
            print("pingServer.Responding")
            self.startingServer = False
            self.serverReady.emit()
        elif self.pingingStartTime.msecsTo(QTime.currentTime()) < serverReadyTimeout:
            print("pingServer.Delay")
            QTimer.singleShot(self.serverPingDelay, self.pingServer)
        else:
            print("pingServer.Kill")
            self.startingServer = False
            self.process.kill()
            self.serverStartingUpError.emit()
            
    def processError(self, error):
        if self.startingServer:
            print("processError.Starting")
            self.startingServer = False
            self.process.kill()
            self.serverStartingUpError.emit(self.tr('Process error during starting up...'))
        elif self.terminatingServer:
            print("processError.terminating")
            if error == QProcess.Crashed:
                print("processError.Crashed")
                return
            self.terminatingServer = False
            self.process.kill()
            self.serverShuttingDownError.emit(self.tr('Error during server termination...'))
        else:
            print("processError.else....")
              
    def processFinished(self):
        if self.startingServer:
            print("processFinished.starting")
            self.startingServer = False
            self.serverStartingUpError.emit(self.tr('Process suddenly died...'))
        elif self.terminatingServer:
            print("processFinished.terminating")
            self.terminatingServer = False
            self.serverTerminated.emit()
        else:
            print("processFinished.emitDied")
            self.serverUnexpectedlyDied.emit(self.tr('Process unexpectedly died...'))
            
    def checkShutdownTimeout(self):
       if not self.terminatingServer:
           print("checkShutdownTimeout.Not terminating")
           return
            
       if self.isServerRunning():
           print("checkShutdownTimeout.Running")
           self.process.kill()
           self.terminatingServer = False
           self.serverShuttingDownError.emit(self.tr('Killing server with fire...'))
       else:
           print("checkShutdownTimeout.Else ...")           

    #---------------------------------------------------------------------------
     

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        
        self.menu = QMenu(parent)
        
        self.startAction   = QAction(self.tr("&Start OpenBCI"), self)
        self.stopAction    = QAction(self.tr("S&top OpenBCI"),  self)
        self.quitAction    = QAction(self.tr("&Close OpenBCI tray"), self)
        self.runGuiAction  = QAction(self.tr("&Run Control Panel..."),  self)
        self.runSvarogAction  = QAction(self.tr("&Run Signal Viewer..."),  self)

        self.runningIcon     = QIcon(qApp.style().standardPixmap(QStyle.SP_ComputerIcon))
        self.startingUpIcon  = QIcon(qApp.style().standardPixmap(QStyle.SP_MessageBoxInformation))
        self.terminatingIcon = QIcon(qApp.style().standardPixmap(QStyle.SP_TrashIcon))
        self.serverDownIcon  = QIcon(qApp.style().standardPixmap(QStyle.SP_MessageBoxCritical))

        self.menu.addAction(self.runGuiAction)
        self.menu.addSeparator()
        self.menu.addAction(self.runSvarogAction)
        self.menu.addSeparator()
        self.menu.addAction(self.startAction)
        self.menu.addAction(self.stopAction)
        #self.menu.addSeparator()
        #self.menu.addAction(self.quitAction)
        
        self.trayIcon = QSystemTrayIcon(self.serverDownIcon)
        self.trayIcon.setContextMenu(self.menu)
        self.trayIcon.show()
        
        self.startAction.triggered.connect(self.startServer)
        self.stopAction.triggered.connect(self.stopServer)
        self.runGuiAction.triggered.connect(self.runGui)
        self.runSvarogAction.triggered.connect(self.runSvarog)
        self.quitAction.triggered.connect(self.quit_tray)

        self.controller = ServerController()
        
        self.trayIcon.setIcon(self.serverDownIcon)
        self.setStoppedUi()
    
        self.guiProcess = QProcess()
        self.svarogProcess = QProcess()
            
        self.controller.serverReady.            connect(self.serverReady)
        self.controller.serverStartingUpError.  connect(self.startingUpError)
        self.controller.serverTerminated.       connect(self.serverTerminated)
        self.controller.serverShuttingDownError.connect(self.shuttingDownError)
        self.controller.serverUnexpectedlyDied. connect(self.serverUnexpectedlyDied)

    #---------------------------------------------------------------------------

    def setEnabledAll(self, enabled):
        self.startAction.setEnabled(enabled)
        self.stopAction.setEnabled(enabled)
        self.runGuiAction.setEnabled(enabled)
        self.runSvarogAction.setEnabled(enabled)
        self.quitAction.setEnabled(enabled)

    def setRunningUi(self, disableAll=False):
        self.startAction.setVisible(False)
        self.stopAction.setVisible(True)
        #self.menu.setDefaultAction(self.stopAction)
        
        if disableAll:
            self.setEnabledAll(False)
        else:
            self.setEnabledAll(True)
       
    def setStoppedUi(self, disableAll=False):
        self.startAction.setVisible(True)
        self.stopAction.setVisible(False)
        self.menu.setDefaultAction(self.startAction)
        
        if disableAll:
            self.setEnabledAll(False)
        else:      
            self.setEnabledAll(True)  
            self.runGuiAction.setEnabled(False)
        
    #---------------------------------------------------------------------------
        
    def startServer(self):
        self.trayIcon.setIcon(self.startingUpIcon)
        self.setRunningUi(disableAll = True)
        self.controller.startServer()
        
    def stopServer(self):
        self.trayIcon.setIcon(self.terminatingIcon)
        self.setStoppedUi(disableAll = True)
        self.controller.stopServer()
        
    #---------------------------------------------------------------------------
       
    def serverReady(self):
        #print 'serverReady'
        self.trayIcon.setIcon(self.runningIcon)
        self.trayIcon.showMessage(self.tr('OBCI tray'),
                                  self.tr('OpenBCI server ready!'),
                                  QSystemTrayIcon.Information,
                                  2*1000)
        self.setRunningUi()

    def startingUpError(self, errorMsg):
        #print 'startingUpError'
        self.trayIcon.setIcon(self.serverDownIcon)
        self.trayIcon.showMessage(self.tr('OpenBCI'),
                                  self.tr('OpenBCI server starting up error: %1.').arg(errorMsg),
                                  QSystemTrayIcon.Critical,
                                  4*1000)
        self.setStoppedUi()
        
    def serverTerminated(self):
        #print 'serverTerminated'
        self.trayIcon.setIcon(self.serverDownIcon)
        self.trayIcon.showMessage(self.tr('OpenBCI'),
                                  self.tr('OpenBCI server terminated.'),
                                  QSystemTrayIcon.Information,
                                  2*1000)
        self.setStoppedUi()
        
    def shuttingDownError(self, errorMsg):
        #print 'shuttingDownError'
        self.trayIcon.setIcon(self.serverDownIcon)
        self.trayIcon.showMessage(self.tr('OpenBCI'),
                                  self.tr('OpenBCI shutting down error: %1.').arg(errorMsg),
                                  QSystemTrayIcon.Critical,
                                  4*1000)
        self.setStoppedUi()
        
    def serverUnexpectedlyDied(self, errorMsg):
        #print 'serverUnexpectedlyDied'
        self.trayIcon.setIcon(self.serverDownIcon)
        self.trayIcon.showMessage(self.tr('OpenBCI'),
                                  self.tr('OpenBCI server unexpectedly died: %1.').arg(errorMsg),
                                  QSystemTrayIcon.Critical,
                                  4*1000)
        self.setStoppedUi()
        
    #---------------------------------------------------------------------------

    def runGui(self):
        #QMessageBox.information(None, self.tr('OpenBCI'), self.tr('RUN GUI'))
        if self.guiProcess.state() == QProcess.NotRunning:
            self.guiProcess.start('obci_gui')

    def runSvarog(self):
        #QMessageBox.information(None, self.tr('OpenBCI'), self.tr('RUN GUI'))
        if self.svarogProcess.state() == QProcess.NotRunning:
            self.svarogProcess.start('svarog')
       
    #---------------------------------------------------------------------------

    def quit_tray(self):
        if not self.controller.isServerRunning():
            qApp.quit()
        else:
            ret = QMessageBox.warning(None, self.tr('OpenBCI'), 
                                      self.tr('Really quit? This will violently kill the server!'),
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)
            if ret == QMessageBox.Yes:
                qApp.quit()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWidget = MainWidget()
    
    #TODO: add parameter to start server by default
    
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
