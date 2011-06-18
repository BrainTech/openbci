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

"""Module defines classes representing smart tag definition. 
Smart tag definition is a data structure defining what kind of bunches of 
samples smart tag is to provide.
By now we have a general, abstract class SmartTagDefinition.

Concrete classes are:
SmartTagEndTagDefinition





SmartTagDurationDefinition

see concrete classes definitions to learn how to use them."""

class SmartTagDefinition(object):
    """An abstract class storing general info. See subclasses defs."""
    def __init__(self, **p_params):
        """Se subclasses defs."""
        self.start_tag_name = p_params['start_tag_name']
        self.start_offset = p_params.get('start_offset', 0.0)
        self.end_offset = p_params.get('end_offset', 0.0)
        self.start_param_func = p_params.get(
            'start_param_func', 
            lambda tag: tag['start_timestamp']
            )
        self.end_param_func = p_params.get(
            'end_param_func', 
            lambda tag: tag['start_timestamp']
            )



class SmartTagEndTagDefinition(SmartTagDefinition):
    """The class is to be used for following requirement:
    'We want to extract bunches of samples starting from some particular
    tag type and ending with some particular tag type.'
    It is a constructor parameter for SmartTagsManager.
    Constructor`s parameters and (at the same time) public slots:
    - start_tag_name - string
    - start_offset - float (default 0)
    - end_offset - float (default 0)
    - end_tags_names - list of strings.

    x = SmartTagEndTagDefinition(start_tag_name='ugm_config', 
                             start_offset=-10.0,
                             end_offset=20.0,
                             end_tags_names=['ugm_config', 'ugm_break'])

    Consider samples file f, and tag scattered on the timeline like that:
    ---100ms------------------300ms-----------400ms---------500ms----------700ms
    ugm_config             ugm_config       ugm_break  ugm_config

    Using x definition means:
    Generate following samples bunches:
    - 90ms;320ms
    - 290ms;420ms
    """
    def __init__(self, **p_params):
        """See class description."""
        super(SmartTagEndTagDefinition, self).__init__(**p_params)
        self.end_tags_names = p_params['end_tags_names']
        
    def is_type(self, p_type):
        """Type check - return true if p_type is end_tag."""
        return p_type == "end_tag"

class SmartTagDurationDefinition(SmartTagDefinition):
    """The class is to be used for following requirement:
    'We want to extract bunches of samples starting from some particular
    tag type and lasting x miliseconds.
    It is a constructor parameter for SmartTagsManager.
    Constructor`s parameters and (at the same time) public slots:
    - start_tag_name - string
    - start_offset - float (default 0)
    - end_offset - float (default 0)
    - duration - float

    x = SmartTagDuration(start_tag_name='ugm_config', 
                             start_offset=-10.0,
                             end_offset=20.0,
                             duration=100.0)

    Consider samples file f, and tag scattered on the timeline like that:
    ---100ms------------------300ms-----------400ms---------500ms-------------
    ugm_config             ugm_config       ugm_break  ugm_config

    Using x definition means:
    Generate following samples bunches:
    - 90ms;220ms
    - 290ms;420ms
    - 490ms;620ms
    """
    def __init__(self, **p_params):
        """See class description."""
        super(SmartTagDurationDefinition, self).__init__(**p_params)
        self.duration = p_params['duration']

    def is_type(self, p_type):
        """Type check - return true if p_type is end_tag."""
        return p_type == "duration"
    pass

