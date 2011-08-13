#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""A heart of ugm. This module implements core classes for ugm to work.
It should be ran as a script in MAIN thread or using UgmEngine.run()."""
import sys
from PyQt4 import QtGui, QtCore, Qt
import Queue
import ugm_config_manager
import ugm_stimuluses

import ugm_logging as logger
LOGGER = logger.get_logger("ugm_engine", "error")

class UgmField(ugm_stimuluses.UgmRectStimulus):
    """For now, just to express it..."""
    pass

class UgmGenericCanvas(QtGui.QWidget):
    """This class represents canvas for ugm, an object holding 
    all stimuluses. As it is simple pyqt widget it might be embedded 
    in some other pyqt elements."""

    def __init__(self, p_parent, p_config_manager):
        """Create widget, create all children from p_config_manager,
        store p_config_manager."""
        QtGui.QWidget.__init__(self, p_parent)
        self.setWindowTitle('UGM')

        self._config_manager = p_config_manager
        self._create_children()

    def _create_children(self):
        """Create ugm fields as children."""
        for i_field_config in self._config_manager.get_ugm_fields():
            UgmField(self, i_field_config)

    def _get_width(self):
        """Return self`s width."""
        return self.frameSize().width()
    def _get_height(self):
        """Return self`s height."""
        return self.frameSize().height()

    def resizeEvent(self, event):
        """Redefine the method so that all children are updated."""
        self.update_geometry()
# --------------------------------------------------------------------------
# -------------- PUBLIC INTERFACE ------------------------------------------
    def get_config_manager(self):
        """Return stored config manager."""
        return self._config_manager

    def update_geometry(self):
        """Update all children. The method is fired explicitly very time 
        config manager changed it`s state and widgets need to be redrawn
        (not rebuilt)."""
        for i in self.children():
            i.update_geometry()

    width = property(_get_width)
    height = property(_get_height)

# -------------- PUBLIC INTERFACE ------------------------------------------
# --------------------------------------------------------------------------

class SpellerWindow(QtGui.QFrame):
    """Main frame using UgmGenericCanvas and other usefull widgets."""
    def __init__(self, p_parent, p_config_manager):
        """Init UgmGenericCanvas and other widgets, lay them out."""
        QtGui.QFrame.__init__(self, p_parent)
        l_hbox = QtGui.QVBoxLayout()
        l_hbox.setContentsMargins(0,0,0,0)

        #self.text = QtGui.QLineEdit()
        #l_hbox.addWidget(self.text)

        self.canvas = UgmGenericCanvas(self, p_config_manager)       
        l_hbox.addWidget(self.canvas)

        self.setLayout(l_hbox)

    def update_geometry(self):
        """Update self`s canvas geometry. Fired when config manager has
        updated it`s state."""
        self.canvas.update_geometry()

class UgmMainWindow(QtGui.QMainWindow):
    """Qt main window for ugm."""
    def __init__(self, p_config_manager):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._config_manager = p_config_manager
        self.view = SpellerWindow(self, p_config_manager)
        self.setCentralWidget(self.view)

    def update(self):
        """Update self`s view.Fired when config manager has
        updated it`s state."""
        self.view.update_geometry()
    def rebuild(self):
        """Delete and once again create self`s central widget."""
        self.view.deleteLater()
        self.view = SpellerWindow(self, self._config_manager)
        self.setCentralWidget(self.view)
        


class UgmEngine(QtCore.QObject):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh."""
    def __init__(self, p_config_manager):
        """Store config manager."""
        super(UgmEngine, self).__init__()
        self._config_manager = p_config_manager
        self.ugm_rebuild = QtCore.pyqtSignal()
        self.connect(self, QtCore.SIGNAL("ugm_rebuild"), 
                     self.ugm_rebuild_signal)

        self.queue = Queue.Queue()
        self.mutex = Qt.QMutex()

    def queue_message(self, l_msg):
        """Insert message to queue waiting to be displayed."""
        self.mutex.lock()
        self.queue.put(l_msg)
        self.mutex.unlock()

    def timer_on_run(self):
        """Fired on run once time."""
        self.update_gui_timer = QtCore.QTimer()
        self.update_gui_timer.connect(self.update_gui_timer,QtCore.SIGNAL("timeout()"),self.timer_update_gui)
        self.update_gui_timer.start(10)


    def timer_update_gui(self):
        """Fired very often - clear self.queue and update gui with those messages."""
        if (self.queue.qsize() > 5):
            LOGGER.info("Warning! Queue size is: "+str(self.queue.qsize()))

        self.mutex.lock()
        while True:
            try:
                msg = self.queue.get_nowait()
            except Queue.Empty:
                break
            else:
                self.update_from_message(
                    msg.type, msg.value)
        self.mutex.unlock()

    def run(self):
        """Fire pyqt application with UgmMainWindow. 
        Refire when app is being closed. (This is justified as if 
        ugm_config_manager has changed its state remarkably main window
        needs to be completely rebuilt."""
        LOGGER.info("ugm_engine run")
        l_app = QtGui.QApplication(sys.argv)
        self._window = UgmMainWindow(self._config_manager)
        self._window.showFullScreen()

        self.on_run_timer = QtCore.QTimer()
        self.on_run_timer.connect(self.on_run_timer,QtCore.SIGNAL("timeout()"),self.timer_on_run)
        self.on_run_timer.setSingleShot(True)
        self.on_run_timer.start(2000) #Todo - need to wait 2 secs?

        l_app.exec_()
        LOGGER.info('ugm_engine main window has closed')

    def update_from_message(self, p_msg_type, p_msg_value):
        """Update ugm from config defined by dictionary p_msg_value.
        p_msg_type must be 0 or 1. 0 means that ugm should rebuild fully,
        2 means that config hasn`t changed its structure, only attributes, 
        so that ugm`s widget might remain the same, 
        they should only redraw."""
        if self._config_manager.update_message_is_full(p_msg_type):
            LOGGER.info('ugm_engine got full message to update.')
            self._config_manager.set_full_config_from_message(p_msg_value)
            self.update_or_rebuild()
            
        elif self._config_manager.update_message_is_simple(p_msg_type):
            LOGGER.info('ugm_engine got simple message to update.')
            self._config_manager.set_config_from_message(p_msg_value)
            self.update()
        else:
            LOGGER.error("Wrong UgmUpdate message type!")
            raise Exception("Wrong UgmUpdate message type!")

    def update_or_rebuild(self):
        """Update or rebuild ugm depending on config manager`s decison..."""
        if self._config_manager.old_new_fields_differ():
            self.rebuild()
        else:
            self.update()

    def update(self):
        """Fired when self._config_manager has changed its state, but only 
        stimuluses`es attributes, not their number or ids."""
        LOGGER.debug("ugm_engine update")
        self._window.update()
    def rebuild(self):
        """Fired when self._config_manager has changed its state 
        considerably - eg number of stimuluses or its ids changed.
        In that situation we need to rebuild gui, not only refresh.
        Send signal, as we need gui to be rebuilt in the main thread."""
        LOGGER.info("ugm_engine rebuild")
        self.emit(QtCore.SIGNAL("ugm_rebuild"))

    def ugm_rebuild_signal(self):
        """See __init__ and rebuild."""
        self._window.rebuild()

if __name__ == '__main__':
    try:
        CONF = sys.argv[1]
    except IndexError:
        CONF = ''
    finally:
        # Run ugm engin from default config or config from prompt
        if CONF == '':
            UgmEngine(ugm_config_manager.UgmConfigManager()).run()
        else:
            UgmEngine(ugm_config_manager.UgmConfigManager(CONF)).run()



