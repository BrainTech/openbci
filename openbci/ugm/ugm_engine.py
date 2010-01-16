#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import ugm_config_manager
import ugm_stimuluses

    
class UgmField(QtGui.QWidget, ugm_config_manager.UgmRectConfig):
    def __init__(self, p_parent, p_config): 
        QtGui.QWidget.__init__(self, p_parent)
        self._ugm_id = p_config['id']
        self._update_geometry_from_config(p_config)
        # TODO - set border to 0
        l_stims_factory = ugm_stimuluses.UgmStimulusFactory()
        for i_stim_config in p_config['stimuluses']:
            l_stims_factory.createStimulus(self, i_stim_config)

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        paint.setBrush(l_bg_color)
        paint.drawRect(0, 0, self.width, self.height)
        paint.end()
    def update_geometry(self):
        """Called from resize event and parent`s update_geometry()."""
        print("update_ugm_field")
        l_config = self.get_config_manager().get_config_for(self._ugm_id)
        self._update_geometry_from_config(l_config)
        for i in self.children():
            i.update_geometry()
    def _update_geometry_from_config(self, p_config):
        self._set_rect_config(self.parent(), p_config)
        self.setGeometry(self.position_x, self.position_y,
                         self.position_x + self.width,
                         self.position_y + self.height)

    def resizeEvent(self, event):
#        self.update_geometry()
        print("resizeEvent UGM FIELD:")
        print(self.parent().geometry())
        print(self.geometry()) 
#        for i in self.children():
#            i.resizeEvent(event)
    def get_config_manager(self):
        return self.parent().get_config_manager()



class UgmGenericCanvas(QtGui.QWidget):
    def __init__(self, p_parent, p_config_manager):
        QtGui.QWidget.__init__(self, p_parent)
        
        #self.setGeometry(0, 0, 1000, 1000) #TODO - chyba trzeba ustawic tego rozmiar
        self._config_manager = p_config_manager
        self.setWindowTitle('Colors')
        
        # Create ugm fields as children
        for i_field_config in self._config_manager.get_ugm_fields():
            UgmField(self, i_field_config)
#        print("GENERIC STIMULUS:")
#        for i in dir(self):
#            print(i)
#        print("JUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUHU")
#        print(self.sizeHint())
#        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
#                           QtGui.QSizePolicy.Expanding)
#        print(self.sizeHint())
#        print(p_parent.geometry()) #TODODODODO
#        print(self.geometry())

    def _get_width(self):
        return self.frameSize().width()
    def _get_height(self):
        return self.frameSize().height()

    def get_config_manager(self):
        return self._config_manager

    def resizeEvent(self, event):
        print("resizeEvent UGMGENERICCANVAS:", event)
        #print(self.parent().geometry())
        #print(self.geometry())
        self.update_geometry()

    def update_geometry(self):
        for i in self.children():
            i.update_geometry()

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

    def resizeEvent(self, event):
        print("resizeEvent SpellerWindow:")
        print(self.geometry())
    def update_geometry(self):
        self.canvas.update_geometry()

class UgmMainWindow(QtGui.QMainWindow):
    def __init__(self, p_config_manager):
        QtGui.QMainWindow.__init__(self)
        self.view = SpellerWindow(self, p_config_manager)
        self.setCentralWidget(self.view)
        self.setWindowTitle('statusbar')

        self.statusBar().showMessage('Ready')

        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(exit)
    def update(self):
        self.view.update_geometry()
        print("update main window")
class UgmEngine(object):
    def __init__(self, p_config_manager):
        self._config_manager = p_config_manager
    def run(self):
        app = QtGui.QApplication(sys.argv)
        self._window = UgmMainWindow(self._config_manager)
        self._window.showFullScreen()
        sys.exit(app.exec_())
    def update(self):
        print("Update ugm engine")
        print(self._config_manager.get_config_for(41))
        self._window.update()

if __name__ == '__main__':
    UgmEngine(ugm_config_manager.UgmConfigManager()).run()

#TODO - 

# - zrobic takie ustawienie zeby fieldy wygladaly juz tak jak trzeba
# - stworzyc mozliwosc modyfikowania ugma online - formaty i identyfikatory

