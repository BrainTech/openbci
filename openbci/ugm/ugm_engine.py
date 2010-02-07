#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import ugm_config_manager
import ugm_stimuluses
import ugm_logging
logger = ugm_logging.get_logger("ugm_engine")

class UgmField(ugm_stimuluses.UgmRectStimulus):
    "For now, just to express it..."
    pass

class UgmGenericCanvas(QtGui.QWidget):
    def __init__(self, p_parent, p_config_manager):
        QtGui.QWidget.__init__(self, p_parent)
        self._config_manager = p_config_manager
        self.setWindowTitle('Colors')
        self._create_children()
    def _create_children(self):
        # Create ugm fields as children
        for i_field_config in self._config_manager.get_ugm_fields():
            UgmField(self, i_field_config)

    def _get_width(self):
        return self.frameSize().width()
    def _get_height(self):
        return self.frameSize().height()

    def get_config_manager(self):
        return self._config_manager

    def resizeEvent(self, event):
        self.update_geometry()

    def update_geometry(self):
        for i in self.children():
            i.update_geometry()
    def update_fully(self):
        logger.debug('ugm_engine.update_fully')
        for i in self.children():
            i.deleteLater()
        self._create_children()
        self.update_geometry()
        #self.update_geometry() # by now
        #TODO - pousuwac wszystkie dzieci i stworzyc je od nowa create_children
        pass

    width = property(_get_width)
    height = property(_get_height)

class SpellerWindow(QtGui.QFrame):
    def __init__(self, parent, p_config_manager):
        QtGui.QFrame.__init__(self, parent)

        hbox = QtGui.QVBoxLayout()
        self.canvas = UgmGenericCanvas(self, p_config_manager)       
        self.text = QtGui.QLineEdit()
        hbox.addWidget(self.text)
        hbox.addWidget(self.canvas)
        self.setLayout(hbox)

    def update_geometry(self):
        self.canvas.update_geometry()
    def update_fully(self):
        self.canvas.update_fully()

class UgmMainWindow(QtGui.QMainWindow):
    def __init__(self, p_config_manager):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('statusbar')
        self.statusBar().showMessage('Ready')
        self._create_widgets(p_config_manager)
    def _create_widgets(self, p_config_manager):
        self.view = SpellerWindow(self, p_config_manager)
        self.mgr = p_config_manager
        self.setCentralWidget(self.view)

#        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
#        exit.setShortcut('Ctrl+Q')
#        exit.setStatusTip('Exit application')
#        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
#
#        menubar = self.menuBar()
#        file = menubar.addMenu('&File')
#        file.addAction(exit)
    def update(self):
        self.view.update_geometry()
    def update_fully(self):
        logger.debug('ugm_engine.UgmMainWindow.update_fully')
        self.view.deleteLater()
        self._create_widgets(self.mgr)
#        self.view.update_fully()

class UgmEngine(object):
    def __init__(self, p_config_manager):
        self._config_manager = p_config_manager
    def run(self):
        app = QtGui.QApplication(sys.argv)
        while True:
            self._window = UgmMainWindow(self._config_manager)
            self._window.showFullScreen()
            app.exec_()
            logger.debug('ugm_engine main window has closed')
#        sys.exit(app.exec_())

    def update_from_message(self, p_msg_type, p_msg_value):
        if self._config_manager.update_message_is_full(p_msg_type):
            self._config_manager.set_full_config_from_message(p_msg_value)
            self._window.close()
#            self.update_fully()
        elif self._config_manager.update_message_is_simple(p_msg_type):
            self._config_manager.set_config_from_message(p_msg_value)
            self.update()
        else:
            raise Exception("Wrong UgmUpdate message type!")
    def update(self):
        self._window.update()
    def update_fully(self):
        self._window.update_fully()

import sys
if __name__ == '__main__':
    try:
        conf = sys.argv[1]
    except:
        conf = ''
    finally:
        if conf == '':
            UgmEngine(ugm_config_manager.UgmConfigManager()).run()
        else:
            UgmEngine(ugm_config_manager.UgmConfigManager(conf)).run()



