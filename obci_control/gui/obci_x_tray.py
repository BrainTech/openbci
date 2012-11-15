#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, subprocess, time
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ServerController(QObject):

    # all values in miliseconds
    serverPingDelay    = 2000
    serverReadyTimeout = 5*serverPingDelay
    serverDiedTiemout = 5*serverPingDelay
    
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

        #self.process.started.connect(self.processStarted)
        
        self.startingStartTime = QTime.currentTime()
        self.terminatingStartTime = QTime.currentTime()
        self.lastResponseTime = QTime.currentTime()

        self.startingServer = False
        self.terminatingServer = False
        self.responding = False

        self.startServer()
        time.sleep(2)
        self.startPinging()

    #---------------------------------------------------------------------------

    def isServerRunning(self):
        try:
            subprocess.check_call(["obci", "info"])
            return True
        except subprocess.CalledProcessError:
            return False
        
    def startServer(self):
        if not self.isServerRunning():
            self.startingStartTime = QTime.currentTime()
            self.startingServer = True
            self.process.start(self.programName)
    
    def stopServer(self):
        if self.isServerRunning():
            print("stopServer.isRunning")
            self.terminatingStartTime = QTime.currentTime()
            self.terminatingServer = True
            os.system('obci srv_kill')
        else:
            print("stopServer.isNotRunning...")
        
    #---------------------------------------------------------------------------

    def startPinging(self):
        QTimer.singleShot(self.serverPingDelay, self.pingServer)
        
    def pingServer(self):
        print("Ping obci server")
        if self.terminatingServer:
            self._terminatingOnPing()
        elif self.startingServer:
            self._startingOnPing()
        elif self.isServerRunning():
            self._runningOnPing()
        else:
            self._notRunningOnPing()

    def _terminatingOnPing(self):
            if not self.isServerRunning():
                print("terminatingOnPing.server not running")
                self.terminatingServer = False
                self.responding = False
                self.serverTerminated.emit()
                QTimer.singleShot(self.serverPingDelay, self.pingServer)
            elif self.terminatingStartTime.msecsTo(QTime.currentTime()) < self.serverReadyTimeout:
                print("terminatingOnPing.Delay")
                self.lastResponseTime = QTime.currentTime()
                self.responding = True
                QTimer.singleShot(self.serverPingDelay, self.pingServer)
            else:
                print("terminatingOnKill.COULD NOT TERMINATE")
                self.terminatingServer = False
                self.serverShuttingDownError.emit(self.tr('Couldn`t shut down OpenBCI. Aborting!!!!!!'))
                return

    def _startingOnPing(self):
            if self.isServerRunning():
                print("startingOnPing.server is running")
                self.startingServer = False
                self.responding = True
                self.lastResponseTime = QTime.currentTime()
                self.serverReady.emit()
                QTimer.singleShot(self.serverPingDelay, self.pingServer)
            elif self.startingStartTime.msecsTo(QTime.currentTime()) < self.serverReadyTimeout:
                print("startingOnPing.Delay")
                QTimer.singleShot(self.serverPingDelay, self.pingServer)
            else:
                print("startingOnPing.COULD NOT START")
                self.startingServer = False
                self.serverStartingUpError.emit(self.tr('Couldn`t start OpenBCI. Aborting!!!!!'))
                return

    def _runningOnPing(self):
            print("runningOnPing.just running")
            self.lastResponseTime = QTime.currentTime()
            if not self.responding:
                self.responding = True
                self.serverReady.emit()                
            QTimer.singleShot(self.serverPingDelay, self.pingServer)

    def _notRunningOnPing(self):
        if self.lastResponseTime.msecsTo(QTime.currentTime()) < self.serverDiedTiemout:
            print("notRunningOnPing.Delay")
            QTimer.singleShot(self.serverPingDelay, self.pingServer)
        else:
            if not self.responding:
                print("notRunningOnPing.Delay passed, just pass....")
                QTimer.singleShot(self.serverPingDelay, self.pingServer)
            else:
                print("notRunningOnPing.Delay passed for the first time")
                self.responding = False
                self.serverUnexpectedlyDied.emit(self.tr('OpenBCI is not responding:('))
                QTimer.singleShot(self.serverPingDelay, self.pingServer)





class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        
        self.menu = QMenu(parent)
        
        self.startAction   = QAction(self.tr("&Start OpenBCI server"), self)
        self.stopAction    = QAction(self.tr("S&top OpenBCI server"),  self)
        self.quitAction    = QAction(self.tr("&Close OpenBCI tray"), self)
        self.runGuiAction  = QAction(self.tr("&Run Control Panel (OpenBCI)..."),  self)
        self.runSvarogAction  = QAction(self.tr("&Run Signal Viewer (Svarog)..."),  self)
        self.runPsychopyAction  = QAction(self.tr("&Run Experiment Designer (Psychopy)..."),  self)
        self.runEeglabAction  = QAction(self.tr("&Run Analysis Tool (EegLab)..."),  self)

        self.runningIcon     = QIcon(qApp.style().standardPixmap(QStyle.SP_ComputerIcon))
        self.startingUpIcon  = QIcon(qApp.style().standardPixmap(QStyle.SP_MessageBoxInformation))
        self.terminatingIcon = QIcon(qApp.style().standardPixmap(QStyle.SP_TrashIcon))
        self.serverDownIcon  = QIcon(qApp.style().standardPixmap(QStyle.SP_MessageBoxCritical))

        self.menu.addAction(self.runGuiAction)
        self.menu.addSeparator()
        self.menu.addAction(self.runSvarogAction)
        self.menu.addSeparator()
        self.menu.addAction(self.runPsychopyAction)
        self.menu.addSeparator()
        self.menu.addAction(self.runEeglabAction)
        self.menu.addSeparator()
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
        self.runPsychopyAction.triggered.connect(self.runPsychopy)
        self.runEeglabAction.triggered.connect(self.runEeglab)
        self.quitAction.triggered.connect(self.quit_tray)

        self.controller = ServerController()
        
        self.trayIcon.setIcon(self.serverDownIcon)
        self.setStoppedUi()
    
        self.guiProcess = QProcess()
        self.svarogProcess = QProcess()
        self.psychopyProcess = QProcess()
        self.eeglabProcess = QProcess()
            
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
        if self.guiProcess.state() == QProcess.NotRunning:
            self.guiProcess.start('obci_gui')

    def runSvarog(self):
        if self.svarogProcess.state() == QProcess.NotRunning:
            self.svarogProcess.start('svarog')

    def runPsychopy(self):
        if self.psychopyProcess.state() == QProcess.NotRunning:
            self.psychopyProcess.start('psychopy')

    def runEeglab(self):
        if self.eeglabProcess.state() == QProcess.NotRunning:
            self.eeglabProcess.start('eeglab')
       
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
