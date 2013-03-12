#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""This moduel defines abstract class for ugm stimulus and concrete classes
defining standard stimuluses. The module is used in ugm_engine module.

Wanna define a new type of stimulus??
- create a subclass of UgmStimulus
- at least define methods _set_config and paintEvent
- add the class to UgmStimulusFactory.create_stimulus
- use new stimulus in ugm config (as described in ugm_config_manager)
"""
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QPoint as P
import os.path


# --------------------------------------------------------------------------
# ----------- Helper classes -----------------------------------------------

class UgmRectConfig(object):
    """A class from which every standar stimulus should inherit
    as it defines method to set rectangle-like widget`s properties,
    so that it can by correctly refreshed in pain event.
    Defined attributes:
    - height
    - width
    - position_x
    - position_y
    - color
    """
    def _set_rect_config(self, p_parent, p_config_dict):
        """Set self`s attributes extracted from p_config_dict.
        Created attributes are:
        - height
        - width
        - position_x
        - position_y
        - color.
        See ugm_config_manger module`s description to learn 
        how to define p_config_dict.
        """
        try:
            self._set_width(p_parent, p_config_dict)
            self._set_height(p_parent, p_config_dict)
            self._set_vertical_position(p_parent, p_config_dict)
            self._set_horizontal_position(p_parent, p_config_dict)
            self._set_color(p_parent, p_config_dict)
        except KeyError, l_exc:
            raise UgmMissingConfigKey(l_exc.args[0], p_config_dict)

    def _set_width(self, p_parent, p_config_dict):
        """Set width."""
        if p_config_dict['width_type'] == 'absolute':
            self.width = p_config_dict['width']
        elif p_config_dict['width_type'] == 'relative':
            self.width = p_parent.width * p_config_dict['width']
        else:
            raise UgmUnknownConfigValue('width_type',
                                        p_config_dict)
    def _set_height(self, p_parent, p_config_dict):
        """Set height."""
        if p_config_dict['height_type'] == 'absolute':
            self.height = p_config_dict['height']
        elif p_config_dict['height_type'] == 'relative':
            self.height = p_parent.height * p_config_dict['height']
        else:
            raise UgmUnknownConfigValue('height_type',
                                        p_config_dict)
    def _set_horizontal_position(self, p_parent, p_config_dict):
        """Set horizontal position."""
        if p_config_dict['position_horizontal_type'] == 'absolute':
            self.position_x = p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'relative':
            self.position_x = p_parent.width * \
                p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'aligned':
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
    def _set_vertical_position(self, p_parent, p_config_dict):
        """.Set vertical position."""
        if p_config_dict['position_vertical_type'] == 'absolute':
            self.position_y = p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'relative':
            self.position_y = p_parent.height * \
                p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'aligned':
            if p_config_dict['position_vertical'] == 'top':
                self.position_y = 0
            elif p_config_dict['position_vertical'] == 'bottom':
                self.position_y = p_parent.height - self.height
            elif p_config_dict['position_vertical'] == 'center':
                self.position_y = p_parent.height/2 - self.height/2
            else:
                raise UgmUnknownConfigValue('position_vertical',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_vertical_type',
                                        p_config_dict)
        
    def _set_color(self, p_parent, p_config_dict):
        """Set color."""
        try:
            self.color = p_config_dict['color']
        except:
            pass

class UgmUnknownConfigValue(Exception):
    """Raised when some stimulus configuration property 
    has unrecognised value."""
    def __init__(self, p_key, p_config_dict):
        """Store key and config."""
        self._key = p_key
        self._config_dict = p_config_dict
    def __str__(self):
        """Return exception message."""
        return ''.join(["Unrecognised config value: ",
                        self._config_dict[self._key],
                        " for key: ",
                        self._key,
                        " from config:\n",
                        str(self._config_dict)])

class UgmMissingConfigKey(Exception):
    """Raised when some required field in 
    stimulus configuration is missing."""
    def __init__(self, p_key, p_config_dict):
        """Store key and config."""
        self._key = p_key

        self._config_dict = p_config_dict
    def __str__(self):
        """Return exception message."""
        return ''.join(["Missing config entry for key: ",
                        self._key,
                        " from config:\n",
                        str(self._config_dict)])


# --------------------------------------------------------------------------
# ----------------- Stimuluses classes -------------------------------------

class UgmStimulusFactory(object):
    """Stimuluses factory - for given definition of stimulus (in dict)
    returns a proper stimulus instance."""
    def create_stimulus(self, p_parent, p_stim_config):
        """Stimuluses factory - for given definition of stimulus (in dict)
        returns a proper stimulus instance. See ugm_config_manager to learn
        how to create stimulus`es definition.
        By now possible stimuluses are:
        - rectangle,
        - image,
        - text."""
        l_stim = p_stim_config['stimulus_type']
        if l_stim == 'feedback':
            return UgmFeedbackStimulus(p_parent, p_stim_config)
        if l_stim == 'maze':
            return UgmMazeStimulus(p_parent, p_stim_config)
        elif l_stim == 'rectangle':
            return UgmRectStimulus(p_parent, p_stim_config)
        elif l_stim == 'image':
            return UgmImageStimulus(p_parent, p_stim_config)
        elif l_stim == 'text':
            return UgmTextStimulus(p_parent, p_stim_config)

class UgmStimulus(QtGui.QWidget):
    """A base, abstract class for every stimulus. It enforces on every
    subclass to define its own method _set_config(). See ugm_engine 
    to learn how stimuluses are used.
    Attributes:
    - _ugm_id
    """
    def __init__(self, p_parent, p_config_dict):
        """Create an instance of soume UgmStimulus`es subclass depending
        on p_config_dict. See ugm_config_manger to learn how to define
        p_config_dict."""
        QtGui.QWidget.__init__(self, p_parent)
        try:
            self._ugm_id = p_config_dict['id']
        except KeyError:
            raise UgmMissingConfigKey('id', p_config_dict)

        self._update_geometry_from_config(p_config_dict)

        l_stims_factory = UgmStimulusFactory()
        # Create other stimuluses positioned inside current stimulus...
        for i_stim_config in p_config_dict['stimuluses']:
            l_stims_factory.create_stimulus(self, i_stim_config)

    def update_geometry(self):
        """Get config for self from config manager, redraw and fire
        update_geometry for every child."""
        l_config = self.get_config_manager().get_config_for(self._ugm_id)
        self._update_geometry_from_config(l_config)
        for i in self.children():
            i.update_geometry()

    def _update_geometry_from_config(self, p_config):
        """Redraw considering p_config dictionary."""
        # Set self`s attributes needed to pisition and draw self.
        self._set_config(self.parent(), p_config)
        # Positioning attributes are set, so we can update self`s geometry
        self.setGeometry(self.position_x, self.position_y,
                         self.position_x + self.width,
                         self.position_y + self.height)
        # Fire update so that paint event is evoked
        self.update()

    def get_config_manager(self):
        """Return ugm_config_manager instance storing config for whole ugm.
        Get it from self`s parent."""
        return self.parent().get_config_manager()


# --------------------------------------------------------------------------
# Below you see classes representing concrete stimuluses ------------------
class UgmFeedbackStimulus(UgmStimulus, UgmRectConfig):
    """Feedback stimulus definition. See ugm_config_manager to see 
    configuration options.
    Attributes:
    (From UgmRectconfig):
    - height
    - width
    - position_x
    - position_y
    - color
    - feedback_level - float in [0;1] representing percentage of 'hit'
    """
    def _set_config(self, p_parent, p_config_dict):
        """Set positioning and presentation configuration 
        from p_config_dict."""

        self._set_rect_config(p_parent, p_config_dict)
        self._feed_level = p_config_dict['feedback_level']
        self._feed_px = self._feed_level * self.height
        self.setContentsMargins(1,1,1,1)

    def paintEvent(self, event):
        """Draw rectangle from attributes set in self _set_config.
        Draw BAR regargind self._feed_px."""
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        if self._feed_level > 0:
            paint.drawRect(0, 0, self.width, self.height)
            paint.setBrush(l_bg_color)
            paint.drawRect(0, self.height-self._feed_px, 
                           self.width, self._feed_px)            
        else:
            paint.drawRect(0, 0, self.width, self.height)
        paint.end()
            

        


class UgmImageStimulus(UgmStimulus, UgmRectConfig):
    """Image stimulus definition. It inherits form UgmRectconfig, 
    as geometry of image stimulus widget is rectangular.
    See ugm_config_manager to see 
    configuration options.
    Attributes:
    - _image
    (From UgmStimulus):
    - _ugm_id
    (From UgmRectconfig):
    - height
    - width
    - position_x
    - position_y
    - color
    """
    def _set_config(self, p_parent, p_config_dict):
        """Set rectangle-like attributes and additional image-specific
        attributes for self, all needed to draw self in paintEnent."""
        try:
            l_image_path = p_config_dict['image_path']
        except KeyError:
            raise UgmMissingConfigKey('image_path', p_config_dict)
        l_image_path = self._determine_real_image_path(l_image_path)
        
        self._image = QtGui.QImage(QtCore.QString(l_image_path))
        if self._image.isNull():
            l_msg = ''.join(['Couldn`t find image from path: "',
                             l_image_path,
                             '" defined in config file.'])
            #raise Exception(l_msg)
            print("EEEEEEEEEEEEEROR:"+l_msg)

        # By now we get image`s size from the image
        p_config_dict['width_type'] = 'absolute'
        p_config_dict['height_type'] = 'absolute'
        p_config_dict['width'] = self._image.size().width()
        p_config_dict['height'] = self._image.size().height()
        self._set_rect_config(p_parent, p_config_dict)

    def _determine_real_image_path(self, p_image_path):
        """For p_image_path return a system path for image.
        p_image_path might be:
        - a string starting with 'ugm.resources.'
        - a string NOT starting with 'ugm.resources.'
        If second, just return that string (assuming that this is 
        an absolute path).
        If first, p_image_path is sth like ugm.resources.file.png
        and we return system-path-to-resources-module + file.png
        """
        prefix = 'obci.gui.ugm.resources.'
        if p_image_path.startswith(prefix):
            # p_image_path is a path like ugm.resources.file.png
            # determine resources/__init__.py path
            m = __import__(prefix,
                           fromlist=['ugm']).__file__
            m_file = os.path.abspath(m[:m.rfind('/')])
            l_file = os.path.join(m_file, p_image_path[len(prefix):])

        else:
            # p_image_path is just a path
            l_file = p_image_path
        return os.path.expanduser(l_file)

    def paintEvent(self, event):
        """Draw image from self._image."""
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.drawImage(0, 0, self._image)
        paint.end()
        
LINES_DISTANCE = 20
class UgmTextStimulus(UgmStimulus, UgmRectConfig):
    """Text stimulus definition. It inherits form UgmRectconfig, 
    as geometry of text stimulus widget is rectangular.
    See ugm_config_manager to see 
    configuration options.
    Attributes:
    - _font
    - _color
    - _message
    (From UgmStimulus):
    - _ugm_id
    (From UgmRectconfig):
    - height
    - width
    - position_x
    - position_y
    - color
    """
    def _set_config(self, p_parent, p_config_dict):
        """Set rectangle-like attributes and additional text-specific
        attributes for self, all needed to draw self in paintEnent."""
        try:
            self._font = QtGui.QFont()
            self._font.setFamily(p_config_dict['font_family'])
            self._font.setPointSize(int(p_config_dict['font_size']))
            self._color = p_config_dict['font_color']
            self._messages = p_config_dict['message'].split('\n')
            if len(self._messages) <= 1:
                self._messages = p_config_dict['message'].split('\\n')                
            l_font_metrics = QtGui.QFontMetrics(self._font)
            p_config_dict['width_type'] = 'absolute'
            p_config_dict['height_type'] = 'absolute'
            p_config_dict['width'] = max([l_font_metrics.width(t) for t in self._messages])
            self._line_height = int(p_config_dict['font_size'])
            p_config_dict['height'] = self._line_height + \
                (self._line_height+LINES_DISTANCE)*(len(self._messages)-1)

            # Or l_font_metrics.height() ??
        except KeyError, l_exc:
            raise UgmMissingConfigKey(l_exc.args[0], p_config_dict)
        self._set_rect_config(p_parent, p_config_dict)
        
    def paintEvent(self, event):
        """Draw text from self._message."""
        paint = QtGui.QPainter()
        paint.begin(self)
        l_color = QtGui.QColor(0, 0, 0)
        l_color.setNamedColor(self._color)
        paint.setPen(l_color)
        paint.setFont(self._font)

        t = self._messages[0]
        paint.drawText(0, self._line_height, t)

        for i, t in enumerate(self._messages[1:]):
            paint.drawText(0, self._line_height+(self._line_height+LINES_DISTANCE)*(i+1), t)

        paint.end()

class UgmRectStimulus(UgmStimulus, UgmRectConfig):
    """Rectangle stimulus definition. See ugm_config_manager to see 
    configuration options.
    Attributes:
    (From UgmRectconfig):
    - height
    - width
    - position_x
    - position_y
    - color
    """
    def _set_config(self, p_parent, p_config_dict):
        """Set positioning and presentation configuration 
        from p_config_dict."""
        self._set_rect_config(p_parent, p_config_dict)

    def paintEvent(self, event):
        """Draw rectangle from attributes set in self _set_config"""
        paint = QtGui.QPainter()
        paint.begin(self)
        l_bg_color = QtGui.QColor(0, 0, 0)
        l_bg_color.setNamedColor(self.color)
        paint.setBrush(l_bg_color)
        # Self`s size is (self.width, self.height) so we paint from (0,0)
        paint.drawRect(0, 0, self.width, self.height)
        paint.end()

        
class UgmMazeStimulus(UgmStimulus, UgmRectConfig):
    """Feedback stimulus definition. See ugm_config_manager to see 
    configuration options.
    Attributes:
    (From UgmRectconfig):
    - height
    - width
    - position_x
    - position_y
    - color
    - feedback_level - float in [0;1] representing percentage of 'hit'
    """
    def _set_config(self, p_parent, p_config_dict):
        """Set positioning and presentation configuration 
        from p_config_dict."""
        self._set_rect_config(p_parent, p_config_dict)

        self._user_x = int(p_config_dict['maze_user_x'])#0-4
        self._user_y = int(p_config_dict['maze_user_y'])#0-4
        self._user_direction = p_config_dict['maze_user_direction'] #
        self._user_color = p_config_dict['maze_user_color'] #NESW
        
        #assume wider than higher
        self._maze_wall_width = 5 #px
        self._maze_zero_x = int((self.width - self.height)/2.0)
        self._maze_zero_y = self._maze_wall_width
        self._maze_size = self.height - self._maze_wall_width*2
        self._maze_field_size = self._maze_size/5

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self._paint_maze(painter)
        self._paint_user(painter)
        painter.end()

    def _paint_maze(self, painter):
        #background
        pen = QtGui.QPen()
        pen.setWidth(5)
        painter.setPen(pen)
        bg_color = QtGui.QColor(0, 0, 0)
        bg_color.setNamedColor(self.color)
        painter.setBrush(bg_color)
        painter.drawRect(self._maze_zero_x, self._maze_zero_y, 
                         self._maze_size, self._maze_size)
        
        #walls - vertical
        x = self._maze_zero_x + 2*(self._maze_field_size)
        y1 = self._maze_zero_y
        y2 = self._maze_zero_y+self._maze_field_size
        painter.drawLine(x,
                         y1,
                         x,
                         y2)
        x = self._maze_zero_x + 3*(self._maze_field_size)
        painter.drawLine(x,
                         y1,
                         x,
                         y2)


        x = self._maze_zero_x + self._maze_field_size
        y1 = self._maze_zero_y + self._maze_field_size
        y2 = self._maze_zero_y + 3*self._maze_field_size
        painter.drawLine(x,
                         y1,
                         x,
                         y2)
        x = self._maze_zero_x + 4*self._maze_field_size
        painter.drawLine(x,
                         y1,
                         x,
                         y2)

        x = self._maze_zero_x + 2*self._maze_field_size
        y1 = self._maze_zero_y + 3*self._maze_field_size
        y2 = self._maze_zero_y + 5*self._maze_field_size
        painter.drawLine(x,
                         y1,
                         x,
                         y2)
        x = self._maze_zero_x + 3*self._maze_field_size
        painter.drawLine(x,
                         y1,
                         x,
                         y2)

        #walls - horizontal
        y = self._maze_zero_y + 2*self._maze_field_size
        painter.drawLine(self._maze_zero_x + self._maze_field_size,
                         y,
                         self._maze_zero_x + 4*self._maze_field_size,
                         y)

        y = self._maze_zero_y + 4*self._maze_field_size
        painter.drawLine(self._maze_zero_x,
                         y,
                         self._maze_zero_x + 2*self._maze_field_size,
                         y)
        painter.drawLine(self._maze_zero_x + 3*self._maze_field_size,
                         y,
                         self._maze_zero_x + 5*self._maze_field_size,
                         y)

        # start
        x = self._maze_zero_x + int(2.5*self._maze_field_size) - 3
        y = self._maze_zero_y + int(4.5*self._maze_field_size) - 3
        for i in range(6):
            painter.drawLine(x,
                             y+i,
                             x+6,
                             y+i)

        # stop
        x1 = self._maze_zero_x + int(2.25*self._maze_field_size)
        x2 = self._maze_zero_x + int(2.75*self._maze_field_size)
        y1 = self._maze_zero_y + int(0.25*self._maze_field_size)
        y2 = self._maze_zero_y + int(0.75*self._maze_field_size)
        painter.drawLine(x1,
                         y1,
                         x2,
                         y2)
        painter.drawLine(x2,
                         y1,
                         x1,
                         y2)

    def _paint_user(self, painter):
        pen = QtGui.QPen()
        pen.setWidth(2)
        painter.setPen(pen)
        user_color = QtGui.QColor(0, 0, 0)
        user_color.setNamedColor(self._user_color)
        painter.setBrush(user_color)
        painter.drawConvexPolygon(*self._get_user_points())
        #painter.drawPoints(*self._get_user_points())

    def _get_user_points(self):
        x = self._user_x
        y = self._user_y
        dir = self._user_direction

        # get bar of 25 points at to-be-user's position
        b = self._get_bar_points(self._maze_zero_x + x*self._maze_field_size, 
                                 self._maze_zero_y + y*self._maze_field_size)

        # choose some points so that user looks like arrow directed to dir
        if dir == 'UP':
            points = [b[2], b[14], b[13], b[23], b[21], b[11], b[10]]
        elif dir == 'RIGHT':
            points = [b[14], b[22], b[17], b[15], b[5], b[7], b[2]]
        elif dir == 'LEFT':
            points = [b[10], b[2], b[7], b[9], b[19], b[17], b[22]]
        else:
            raise Exception("UGM MAZE ERROR - Unrecognised user direction: "+str(dir))

        return points
        
    def _get_bar_points(self, x_off, y_off):
        #1/6 away from from field's edge 
        x = self._maze_field_size/6
        y = self._maze_field_size/6

        # size of bar's step
        size = self._maze_field_size - 2*x

        # nuber of bar's steps
        step = size/4

        #add offset - position bar in proper place on canvas
        x = x + x_off
        y = y + y_off

        #create bar
        points = []
        for i in range(5):
            for j in range(5):
                points.append(P(x+j*step, y+i*step))

        return points
                         
