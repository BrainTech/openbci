
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
        elif l_stim == 'image':
            return UgmImageStimulus(p_parent, p_stim_config)
        elif l_stim == 'text':
            return UgmTextStimulus(p_parent, p_stim_config)

class UgmStimulus(QtGui.QWidget):
    def __init__(self, p_parent, p_config_dict):
        QtGui.QWidget.__init__(self, p_parent)
        self._ugm_id = p_config_dict['id']
        self._update_geometry_from_config(p_config_dict)
    def resizeEvent(self, event):
        print("stumuls resize event")
#        self.update_geometry()
#        print("resizeEvent UGM STIMULUS:")
#        print(self.parent().geometry())
#        print(self.geometry())  
    def update_geometry(self):
        """Called from resize event."""
        print("UUUUUUUUUUUUUUUUUUUUUUUUUUUUPADE STIMULUS")
        l_config = self.get_config_manager().get_config_for(self._ugm_id)
        self._update_geometry_from_config(l_config)
    def _update_geometry_from_config(self, p_config):
        self._set_config(self.parent(), p_config)
        # Below I must call the method every time, as we need to
        # refresh stimuli after refreshing UgmField
        self.setGeometry(0, 0, self.parent().width, self.parent().height)
        self.update()

    def get_config_manager(self):
        return self.parent().get_config_manager()

class UgmImageStimulus(UgmStimulus, ugm_config_manager.UgmRectConfig):
    # TODO - teraz podaje sie width i height, na tej podstawie liczy sie position ... pewnie na razie width i height powinny sie brac z obrazka i juz ...
    def _set_config(self, p_parent, p_config_dict):
        #TODO - set default config values
        self._image_path = p_config_dict['image_path']
        self._image = QtGui.QImage(QtCore.QString(self._image_path))
        # By now we get image`s size from the image
        p_config_dict['width_type'] = 'absolute'
        p_config_dict['height_type'] = 'absolute'
        p_config_dict['width'] = self._image.size().width()
        p_config_dict['height'] = self._image.size().height()
        self._set_rect_config(p_parent, p_config_dict)

    def paintEvent(self, event):
        print("IMAGE PAINT EVEEEEEEEEEEN")
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.drawImage(self.position_x, self.position_y, self._image)
        paint.end()
        
class UgmTextStimulus(UgmStimulus, ugm_config_manager.UgmRectConfig):
    def _set_config(self, p_parent, p_config_dict):
        self._font = QtGui.QFont()
        self._font.setFamily(p_config_dict['font_family'])
        self._font.setPointSize(p_config_dict['font_size'])
        self._color = p_config_dict['font_color']
        self._message = p_config_dict['message']

        l_font_metrics = QtGui.QFontMetrics(self._font)
        p_config_dict['width_type'] = 'absolute'
        p_config_dict['height_type'] = 'absolute'
        p_config_dict['width'] = l_font_metrics.width(self._message)
        p_config_dict['height'] = p_config_dict['font_size']#l_font_metrics.height() #TODO - na pewno tak?
        self._set_rect_config(p_parent, p_config_dict)
        
    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        l_color = QtGui.QColor(0, 0, 0)
        l_color.setNamedColor(self._color)
    	paint.setPen(l_color)
        paint.setFont(self._font)
        paint.drawText(self.position_x,
                       self.position_y + self.height, self._message)
        paint.end()
    #TODO
    pass
class UgmRectStimulus(UgmStimulus, ugm_config_manager.UgmRectConfig):
    def _set_config(self, p_parent, p_config_dict):
        #TODO - set default config values
        self._set_rect_config(p_parent, p_config_dict)

    def paintEvent(self, event):
        print("RECT PAINT EVEEEEEEEEEEN")
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        paint.setBrush(l_bg_color)
        
        paint.drawRect(self.position_x, self.position_y, self.width, self.height)
        paint.end()

