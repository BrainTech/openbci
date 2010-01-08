
from PyQt4 import QtGui, QtCore
import ugm_config_manager

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
        self._ugm_id = p_config_dict['id']
        self._update_geometry_from_config(p_config_dict)
    def resizeEvent(self, event):
        self._update_geometry()
        print("resizeEvent UGM STIMULUS:")
        print(self.parent().geometry())
        print(self.geometry())
    def _update_geometry(self):
        pass #TODO pobirac z jakiegos globalnego manager config dla siebie i zmieniac swoje rozmiary    
    def _update_geometry(self):
        """Called from resize event."""
        l_config = self.get_config_manager().get_config(self._ugm_id)
        self._update_geometry_from_config(l_config)
    def _update_geometry_from_config(self, p_config):
        self._set_config(self.parent(), p_config)
        # Below I must call the method every time, as we need to
        # refresh stimuli after refreshing UgmField
        self.setGeometry(0, 0, self.parent().width, self.parent().height)

    def get_config_manager(self):
        return self.parent().get_config_manager()

class UgmRectStimulus(UgmStimulus, ugm_config_manager.UgmRectConfig):
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
