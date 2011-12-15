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
"""This moduel defines abstract class for ugm stimulus and concrete classes
defining standard stimuluses. The module is used in ugm_engine module.

Wanna define a new type of stimulus??
- create a subclass of UgmStimulus
- at least define methods _set_config and paintEvent
- add the class to UgmStimulusFactory.create_stimulus
- use new stimulus in ugm config (as described in ugm_config_manager)
"""
from PyQt4 import QtGui, QtCore


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
            raise Exception(l_msg)

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
        if p_image_path.startswith('ugm.resources.'):
            # p_image_path is a path like ugm.resources.file.png
            # determine resources/__init__.py path
            l_mod_file = __import__('ugm.resources', 
                                    fromlist=['ugm']).__file__
        # determine resources/ dir path
            l_mod_file = l_mod_file[:-len('__init__.pyc')] 
        # determine full file.png path
            l_mod_file = ''.join([l_mod_file,
                                  p_image_path[len('ugm.resources.'):]])
            return l_mod_file
        else:
            # p_image_path is just a path
            return p_image_path

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
            

        
