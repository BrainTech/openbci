#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

"""Module to handle ugm configuration.
Public interface (for UgmConfigManager):
CONFIG FILE HANDLING:
- update_from_file()
- update_to_file()

GETTERS:
- get_config_for()
- get_ugm_fields()
- get_attributes_config()

SETTERS:
- set_full_config()
- set_config()

UGM_UPDATE_MESSAGE handling:
- set_config_from_message()
- set_full_config_from_message()
- config_from_message()
- config_to_message()
- update_message_is_full()
- update_message_is_simple()
- old_new_fields_differ()
"""
import copy
import os, os.path, sys
import pickle
class UgmAttributesManager(object):
    """Manager possible keys and values for config.
    Attributes:
    - attributes_def - define all possible config keys and 
    all possible values for every key
    - attributes_for_elem - define all required keys for every stimulus type
    """
    def __init__(self):
        self.attributes_def = {
            'id':{'value':'int'}, # Required for every stimulus, 
            # used for identyfication while updating

            'width_type':{'value':['absolute', 'relative']}, 
            # Determines how to interpret 'width' property and consequently
            # how to compute stimulus`es width.
            # 'absolute' = width is stimulus`es real width in pixels
            # 'relative' = width is a float representing a fraction of 
            # stimulus`es parent`s width to be computed from. Eg. if width
            # = 0.25 then real width is 1/4 of stimulus`es parent`s width.

            'width':{'value':'float'},
            # Stimulus`es real or fraction width depending on 'width_type'

            'height_type':{'value':['absolute', 'relative']},
            # Same as width_type

            'height':{'value':'float'},
            # Same as width
            
            'position_horizontal_type':{
                'value':['absolute', 'relative', 'aligned']},
            # Type of horizontal positioning. It defines how to interpret
            # 'position_horizontal' property.
            #
            # 'absolute' = 'position_horizontal' is stimulus`es top-left
            # corner`s absolute (in pixels) horizontal distance from 
            # parent`s top-left corner
            #
            # 'relative' = 'position_horizontal' is stimulus`es top-left
            # corner`s horizontal distance from parent`s top-left corner
            # computed as a fraction of parent`s absolute width; eg
            # if 'position_horizontal' = 0.25 then self`s top-left corner
            # is located 0.25*(self`s parent`s width) pixels from 
            # self`s parent`s top-left corner
            #
            # 'aligned' - stimulus is aligned relative to its parent.
            # eg. to left, right, center.

            'position_horizontal':{
                'value':['int', 'float', ['left','center','right']],
                'depend_from':'position_horizontal_type'},
            # For every corresponding position_horizontal_type define its
            # value types

            'position_vertical_type':{
                'value':['absolute', 'relative', 'aligned']},
            # Same as position_horizontal_type

            'position_vertical':{
                'value':['int', 'float', ['top','center','bottom']],
                'depend_from':'position_vertical_type'},
            # Same as position_horizontal

            'color':{'value':'color'},
            # Stimulus`es background color (in format #222111)

            'stimulus_type':{'value':['rectangle', 'image', 'text']},
            # Stimulus`es type

            'image_path':{'value':'string'},
            # A path to stimulus`es image (used by UgmImageStimulus)
            # It migth be just a path or path like ugm.resources.file.png.
            # In this second situation a file will be searched in resources
            # directory in ugm package.
            
            'message':{'value':'string'},
            # A text message of UgmTextStimulus

            'font_family':{'value':'font'},
            # Font family (as string) for UgmTextStimulus

            'font_color':{'value':'color'},
            # Font color (in format #222111) for UgmTextStimulus

            'font_size':{'value':'int'},
            # Font size for UgmTextStimulus

            'stimuluses':{'value':'list'},
            # A list of child stimuluses for current stimulus.
            # It is reasonable, as we might want to position some stimuluses
            # relative to other specific 'containing' stimuluses

            'feedback_level':{'value':'float'}
            # Feedback level for feedback stimulus (float in [0;1]

            }
	# TODO: Stimuluses as attribute?
        self.attributes_for_elem = {
	        'field':['id', 'width_type', 'width', 'height_type',
                     'height', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'color'],
            'rectangle':['id', 'width_type', 'width', 'height_type',
                         'height', 'position_horizontal_type',
                         'position_horizontal', 'position_vertical_type',
                         'position_vertical', 'color'],
            'image':['id', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'image_path'],
            'text':['id', 'position_horizontal_type',
                    'position_horizontal', 'position_vertical_type',
                    'position_vertical', 'message', 'font_family',
                    'font_size', 'font_color'],
            'feedback':['id', 'width_type', 'width', 'height_type',
                         'height', 'position_horizontal_type',
                         'position_horizontal', 'position_vertical_type',
                         'position_vertical', 'color', 'feedback_level']

                
            }

class UgmConfigManager(object):
    """Manage ugm stimuluses configuration. Handle file storing and 
    in-memory representation.
    Attributes:
    - _config_file - string representing config file as 
    python module path, eg ugm.configs.ugm_config
    (for file ...../ugm/configs/ugm_config.py)
    - _fields = a python-list taken from config file representing ugm config
    """
    def __init__(self, p_config_file='ugm_config', p_standard_directory=True):
        """Init manager from config in format 
        package.subpackage...module_with_configuration."""
        self._config_file = p_config_file
        self._standard_config = p_standard_directory
        self._standard_config_dir = ''.join([
                os.path.split(os.path.realpath(os.path.dirname(__file__)))[0], 
                os.path.sep, 'ugm', os.path.sep, 'configs', os.path.sep])

        self._fields = []
        self._old_fields = []
        self.update_from_file(p_standard_config=self._standard_config)
    # ----------------------------------------------------------------------
    # CONFIG FILE MANAGMENT ------------------------------------------------
    def update_from_file(self, p_config_file=None, p_standard_config=False):
        """Import config file from p_config_file or self._config_file
        if p_config_file is None. If we have config in file xxxx.py then
        p_config_file should be a string in format:
        xxxx or aaa.bbb.xxxx if file xxxx.py is in package aaa.bbb."""
        self._standard_config = p_standard_config
        if p_config_file:
            self._config_file = p_config_file
        l_config_fields = self._get_module_from_config(self._config_file)
        ## FIX FIX FIX FIX FIX
        ## FIX FIX FIX FIX FIX
#        l_config_fields.insert(0, {'width_type': 'absolute', 'position_horizontal': 0, 'color': '#000000', 'height_type': 'absolute', 'height': 9999.0, 'width': 9999.0, 'position_horizontal_type': 'absolute', 'stimuluses': [], 'position_vertical': 0, 'id': 0, 'position_vertical_type': 'absolute'})
        ## FIX FIX FIX FIX FIX
        ## FIX FIX FIX FIX FIX
        #reload(l_config_module) # To be sure that the file is imported
        self.set_full_config(l_config_fields)

    def update_to_file(self, p_config_file=None, p_standard_config=False):
        """Write self`s configuration stored in self._fields to file
        defined by path p_config_file or to self._config_file if
        p_config_file is not defined. p_config_file should be a path
        to the file, eg. 'a/b/c/config.py'."""
        if p_config_file:
            l_config_file = p_config_file
            l_standard_config = p_standard_config
        else:
            l_config_file = self._config_file
            l_standard_config = self._standard_config
        
        if l_standard_config:
            l_file_path = self._standard_config_dir + l_config_file + '.ugm'
        else:
            l_file_path = l_config_file
        l_file = open(unicode(l_file_path), 'wb') #TODO -try except
        pickle.dump(self._fields, l_file)
        l_file.close()
    
    def _get_module_from_config(self, p_config_file):
        """ For given string p_config_file representing config file
        in format aaa.bbb.ccc return module instance representing the file
        """
        #TODO update docstrings
        if self._standard_config:
            l_file_path = self._standard_config_dir + self._config_file + '.ugm'
        else:
            l_file_path = self._config_file
        l_file = open(unicode(l_file_path), 'rb') # TODO add try except
        l_fields = pickle.load(l_file)
        l_file.close()
            
        return l_fields

    # CONFIG FILE MANAGMENT ------------------------------------------------
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # PUBLIC GETTERS -------------------------------------------------------
    def get_config_for(self, p_id):
        """Return configuration dictionary for stimulus with p_id id."""
        return copy.deepcopy(self._configs(p_id))

    def get_ugm_fields(self):
        """Return a list of dictionaries representing configuration
        of every UgmField.
        Notice, that we don`t return in-memory list, but we return 
        a deep copy, as gui might want to alter config while processing."""
        return copy.deepcopy(self._fields)
    def get_attributes_config(self):
        """See UgmAttributesManager."""
        l_mgr = UgmAttributesManager()
        return {'attributes_def':
                    l_mgr.attributes_def,
                'attributes_for_elem':
                    l_mgr.attributes_for_elem
                }
    # PUBLIC GETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------
    def _configs(self, p_id):
        """Return configuration dictionary for stimulus with p_id id."""
        return self._get_recursive_config(self._fields, p_id)
    def _get_recursive_config(self, p_fields, p_id):
        """Return configuration dictionary for stimulus with p_id id. 
        Internal method used by _config"""
        for i in p_fields:
            if i['id'] == p_id:
                return i
            j = self._get_recursive_config(i['stimuluses'], p_id)
            if j != None:
                return j
        return None
    def _get_recursive_configs(self, p_fields):
        l_ret_dict = dict()
        self._int_get_recursive_configs(p_fields, l_ret_dict)
        return l_ret_dict

    def _int_get_recursive_configs(self, p_fields, l_ret_dict):      
        for i in p_fields:
            l_ret_dict[i['id']] = i
            self._int_get_recursive_configs(i['stimuluses'], l_ret_dict)
    def _update_old_fields(self):
        """Set _old_fields to _fields."""
        self._old_fields = self._fields
        
    # ----------------------------------------------------------------------
    # PUBLIC SETTERS -------------------------------------------------------
    def set_full_config(self, p_config_fields):
        """Set self`s in-memory ugm configuration to p_config_fields 
        being a list of dictionaries representin ugm stimuluses."""
        self._update_old_fields()
        self._fields = p_config_fields

    def set_full_config_from_message(self, p_msg):
        """Set self`s in-memory ugm configuration based on a list of 
        dictionaries extracted from p_msg string representing it."""
        l_full_config = self.config_from_message(p_msg)
        self.set_full_config(l_full_config)

    def set_config(self, p_elem_config):
        """Update config for stimulus with id p_elem_config['id'].
        For dictionary representing that stimulus override attributes
        defined id p_elem_config."""
        # Don`create a new entry, use existing one so 
        # that corresponding element in self._fields is also updated
        self._update_old_fields()
        l_elem = self._configs(p_elem_config['id'])
        for i_key, i_value in p_elem_config.iteritems():
            l_elem[i_key] = i_value

    def set_configs(self, p_elem_configs):
        for i_config in p_elem_configs:
            self.set_config(i_config)

    def set_config_from_message(self, p_msg):
        """Update config for stimuluses with data extracted 
        from p_msg string representing it."""

        l_configs = self.config_from_message(p_msg)
        self.set_configs(l_configs)

    # PUBLIC SETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------
    def update_message_is_full(self, p_msg_type):
        """Return true if p_msg_type represents full_update_message."""
        return p_msg_type == 0
    def update_message_is_simple(self, p_msg_type):
        """Return true if p_msg_type represents simple update message."""
        return p_msg_type == 1
    def old_new_fields_differ(self):
        """Return true if self._old_fields and self._fields 
        are different."""

        l_olds = self._get_recursive_configs(self._old_fields)
        l_news = self._get_recursive_configs(self._fields)
        l_first = self._old_new_fields_differ_helper(l_olds, l_news)
        if not l_first:
            return self._old_new_fields_differ_helper(l_news, l_olds)
        else:
            return l_first
    def _old_new_fields_differ_helper(self, l_olds, l_news):
        for i_old_key, i_old_value in l_olds.iteritems():
            try:
                #TODO this in unnesesary
                l_new_value = l_news[i_old_key]
            except KeyError:
                return True
            else:
                # None, as 'fields' don`t have 'type' attribute
                if l_new_value.get('type', None) != \
                        i_old_value.get('type', None):
                    return True
        return False
    def config_from_message(self, p_msg):
        """Create python configuration structure 
        from message string p_msg."""
        return eval(p_msg)
    def config_to_message(self):
        """Create and return string from self`s configuration structure."""
        return str(self._fields)
