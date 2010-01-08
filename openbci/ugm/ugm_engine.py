#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import ugm_config_manager

class UgmUnknownConfigValue(Exception):
    def __init__(self, p_key, p_config_dict):
        self._key = p_key
        self._config_dict = p_config_dict
    def __str__(self):
        return ''.join(["Unrecognised config value: ",
                        self._config_dict[self._key],
                        " for key: ",
                        self._key,
                        " from config:\n",
                        str(self._config_dict)])

class UgmStimulusFactory(object):
    #TODO - create a cool list with factories for every stimulus
    def createStimulus(self, p_parent, p_stim_config):
        l_stim = p_stim_config['stimulus_type']
        if l_stim == 'rectangle':
            return UgmRectStimulus(p_parent, p_stim_config)
        elif l_stim == 'cross':
            return UgmCrossStimulus(p_parent, p_stim_config)

class UgmStimulus(QtGui.QWidget):
    def __init__(self, p_parent, p_config_dict):
        QtGui.QWidget.__init__(self, p_parent)
        self._set_config(p_parent, p_config_dict)
        self.setGeometry(0, 0, p_parent.width, p_parent.height)
    def resizeEvent(self, event):
        self._update_geometry()
        print("resizeEvent UGM STIMULUS:")
        print(self.parent().geometry())
        print(self.geometry())
    def _update_geometry(self):
        pass #TODO pobirac z jakiegos globalnego manager config dla siebie i zmieniac swoje rozmiary
    def get_config_manager(self):
        return self.parent().get_config_manager()


class UgmRectConfig(object):
    def _set_rect_config(self, p_parent, p_config_dict):
        #set width
        if p_config_dict['width_type'] == 'absolute':
            self.width = p_config_dict['width']
        elif p_config_dict['width_type'] == 'relative':
            self.width = p_parent.width / p_config_dict['width']
        else:
            raise UgmUnknownConfigValue('width_type',
                                        p_config_dict)

        #set height
        if p_config_dict['height_type'] == 'absolute':
            self.height = p_config_dict['height']
        elif p_config_dict['height_type'] == 'relative':
            self.height = p_parent.width / p_config_dict['height']
        else:
            raise UgmUnknownConfigValue('height_type',
                                        p_config_dict)
        
        #set horizontal position
        if p_config_dict['position_horizontal_type'] == 'absolute':
            self.position_x = p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'relative':
            self.position_x = p_parent.width / p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'aligned': #TODO - alligned? aligned?
            if p_config_dict['position_horizontal'] == 'left':
                self.position_x = 0
            elif p_config_dict['position_horizontal'] == 'right':
                self.position_x = p_parent.width - self.width
            elif p_config_dict['position_horizontal'] == 'center':
                self.position_x = p_parent.width/2 - self.width/2
            else:
                raise UgmUnknownConfigValue('position_horizontal',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_horizontal_type',
                                        p_config_dict)

       #set vertical position
        if p_config_dict['position_vertical_type'] == 'absolute':
            self.position_y = p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'relative':
            self.position_y = p_parent.height / p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'aligned': #TODO - alligned? aligned?
            if p_config_dict['position_vertical'] == 'top':
                self.position_y = 0
            elif p_config_dict['position_vertical'] == 'bottom':
                self.position_y = p_parent.width - self.height
            elif p_config_dict['position_vertical'] == 'center':
                self.position_y = p_parent.height/2 - self.height/2
            else:
                raise UgmUnknownConfigValue('position_vertical',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_vertical_type',
                                        p_config_dict)
            
            
        #set color
        self.color = p_config_dict['color']

    
class UgmRectStimulus(UgmStimulus, UgmRectConfig):
    def _set_config(self, p_parent, p_config_dict):
        #TODO - set default config values
        self._set_rect_config(p_parent, p_config_dict)

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        paint.setBrush(l_bg_color)
        paint.drawRect(self.position_x, self.position_y, self.width, self.height)
        paint.end()
        
class UgmTextStimulus(UgmStimulus):
    #TODO
    pass

class UgmImageStimulus(UgmStimulus):
    #TODO
    pass

class UgmField(QtGui.QWidget, UgmRectConfig):
    def __init__(self, p_parent, p_config_dict, p_stims): 
        QtGui.QWidget.__init__(self, p_parent)
        self._set_rect_config(p_parent, p_config_dict)
        self.setGeometry(self.position_x, self.position_y,
                         self.position_x + self.width,
                         self.position_y + self.height)
        # TODO - set border to 0
        l_stims_factory = UgmStimulusFactory()
        for i_stim_config in p_stims:
            l_stims_factory.createStimulus(self, i_stim_config)

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        paint.setBrush(l_bg_color)
        paint.drawRect(0, 0, self.width, self.height)
        paint.end()
    def _update_geometry(self):
        pass #TODO pobirac z jakiegos globalnego manager config dla siebie i zmieniac swoje rozmiary
    def resizeEvent(self, event):
        self._update_geometry()
        print("resizeEvent UGM FIELD:")
        print(self.parent().geometry())
        print(self.geometry()) 
        for i in self.children():
            i.resizeEvent(event)

    def get_config_manager(self):
        return self.parent().get_config_manager()
class UgmGenericCanvas(QtGui.QWidget):
    def __init__(self, p_parent, p_config_manager):
        QtGui.QWidget.__init__(self, p_parent)
        
        #self.setGeometry(0, 0, 1000, 1000) #TODO - chyba trzeba ustawic tego rozmiar
        self._config_manager = p_config_manager
        self.setWindowTitle('Colors')
        #for i in dir(self):
        #    print(i)
        h = 100
        w = 100
        d = {
            'width_type':'absolute',
            'width':w, 
            'height_type':'absolute',
            'height':h,
            'position_horizontal_type':'absolute',
            'position_horizontal':0,
            'position_vertical_type':'absolute',
            'position_vertical':0,
            'color':'#d4d4d4'
            }

        stims = [
            {
                'width_type':'absolute',
                'width':70, 
                'height_type':'absolute',
                'height':70, 
                'position_horizontal_type':'absolute',
                'position_horizontal':0,
                'position_vertical_type':'absolute',
                'position_vertical':0,
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
             },
            {
                'width_type':'absolute',
                'width':60, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'relative',
                'position_horizontal':3,
                'position_vertical_type':'relative',
                'position_vertical':3, 
               'color':'#000000', 
                'stimulus_type':'rectangle'
             }
            ]
        UgmField(self, d, stims)

        d = {
            'width_type':'absolute',
            'width':w, 
            'height_type':'absolute',
            'height':h,
            'position_horizontal_type':'absolute',
            'position_horizontal':0,
            'position_vertical_type':'absolute',
            'position_vertical':100,
            'color':'#eee4d4'
            }
        stims = [
            {
                'width_type':'absolute',
                'width':60, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'right',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
                },
            {
                'width_type':'relative',
                'width':2, 
                'height_type':'relative',
                'height':2, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'bottom',
                'color':'#000000', 
                'stimulus_type':'rectangle'
                }

            ]
        UgmField(self, d, stims)

        d = {
            'width_type':'absolute',
            'width':w, 
            'height_type':'absolute',
            'height':h,
            'position_horizontal_type':'absolute',
            'position_horizontal':100,
            'position_vertical_type':'absolute',
            'position_vertical':100,
            'color':'#eeefff'
            }
        UgmField(self, d, [])
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

    def resizeEvent(self, event):
        print("resizeEvent UGMGENERICCANVAS:")
        print(self.parent().geometry())
        print(self.geometry())
        for i in self.children():
            i.resizeEvent(event)

    def _get_width(self):
        return self.frameSize().width()
    def _get_height(self):
        return self.frameSize().height()
    def get_config_manager(self):
        return self._config_manager
    width = property(_get_width)
    height = property(_get_height)

class SpellerWindow(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)

        hbox = QtGui.QVBoxLayout()
        l_config_manager = ugm_config_manager.UgmConfigManager()
        self.canvas = UgmGenericCanvas(self, l_config_manager)       
        self.text = QtGui.QLineEdit()
        hbox.addWidget(self.text)
        hbox.addWidget(self.canvas)
        self.setLayout(hbox)

    def resizeEvent(self, event):
        print("resizeEvent SpellerWindow:")
        print(self.geometry())

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.view = SpellerWindow(self)
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

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.showFullScreen()
    sys.exit(app.exec_())


#TODO - 
# - ustawic rozmiar ugm generic canvas tak zeby fieldy mogly ustawiac swoje relatywne polozenie
# - zrobic takie ustawienie zeby fieldy wygladaly juz tak jak trzeba
# - zrobic stimulus text i image
# - przeniesc konfiguracje do pliku konfiguracyjnego
# - stworzyc mozliwosc modyfikowania ugma online - formaty i identyfikatory

