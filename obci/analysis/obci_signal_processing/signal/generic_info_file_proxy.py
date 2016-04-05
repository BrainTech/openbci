# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#
import os.path
import xml.dom.minidom
import signal_logging as logger
import signal_exceptions
from .. import types_utils
LOGGER = logger.get_logger("generic_info_file_proxy")


"""Below we have tags definitions - for every tag we have entry in format:
'tag_universal_name': (tag_type('list' or 'simple'), 
                       list of tag translations (one element for 'simple'
                                                 two elemenso for 'list')
                       )
"""
TAGS_DEFINITIONS = {
            'channels_names':
                ('list', ['channelLabels', 'label']),
            'channels_numbers':
                ('list', ['channelNumbers', 'number']),
            'channels_gains':
                ('list', ['calibrationGain', 'calibrationParam']),
            'channels_offsets':
                ('list', ['calibrationOffset', 'calibrationParam']),
            'number_of_samples':
                ('simple', ['sampleCount']),
            'number_of_channels':
                ('simple', ['channelCount']),
            'sampling_frequency':
                ('simple', ['samplingFrequency']),
            'first_sample_timestamp':
                ('simple', ['firstSampleTimestamp']),
            'file':
                ('simple', ['sourceFileName']),
            'file_format':
                ('list', ['sourceFileFormat', 'rawSignalInfo']),
            'calibration': 
            ('simple', ['calibration']),
            'sample_type': 
            ('simple', ['sampleType']),
            'byte_order': 
            ('simple', ['byteOrder']),
            'page_size': 
            ('simple', ['pageSize']),
            'blocks_per_page': 
            ('simple', ['blocksPerPage']),
            'export_file_name': 
            ('simple', ['exportFileName']),
            'export_date': 
            ('simple', ['exportDate'])
            }

class OpenBciDocument(xml.dom.minidom.Document, object):
    """Abstract class for future developement, used in proxies."""
    pass

class GenericInfoFileWriteProxy(object):
    """A class that is responsible for implementing logics of openbci 
    signal parameters storage in info file.
    The file is supposed to be compatible with signalml2.0. By now it isn`t:)
    The class should be separated from all multiplexer-stuff logics.
    InfoFileProxy represents a process of saving one signal parameters.
    Init method gets a dictionary of signal params in format understadable by InfoFileProxy. See __init__ metod for more details.
    Wanna extend info file with a new param? See __init__ method for more details.
    Public interface:
    - finish_saving()
    """
    def __init__(self, p_file_path):
        """Init xml structure. """

        self._file_path = p_file_path
        #TODO works in windows and linux on path with spaces?
        self._xml_factory = self._create_xml_factory()
        #an object useful in the future to easily create xml elements
        self._create_xml_root()
        self._create_tags_controls()
    
    def _create_xml_factory(self):
        return OpenBciDocument()

    def set_attributes(self, p_attrs_dict):
        """For every pair key-> value in p_attrs_dict create tag.
        The type of tag depends on self._tags_control."""
        for i_key, i_value in p_attrs_dict.iteritems():
            self._set_tag(i_key, i_value)

    def finish_saving(self, p_signal_params={}):
        """Write xml_doc to the file, return the file`s path.
        Arguments:
        - p_file_name - a name of to-be-created info file
        - p_dir_path - a dir-path where p_file_name is to be created
        - p_signal_params - a dictionary of all signal parameters that should be stored in info file.

        What is the logics flow of analysing parameters?
        p_signal_params has keys representing signal parameters identificators. 
        self._create_tags_controls creates a dictionary with the same keys, values are functions being 'able' to understand particular param values.
        Method self._process_signal_params, for every key in p_signal_params fires corresponding function from self._tags_control, 
        giving as argument value from p_signal_params...

        So, how can I implement a new parameter usage? Let`s say that the parameter is signal`s colour. Let`s call it 'color', values are strings.
        p_signal_params should contain a pair 'color' -> 'color_value'.
        1. Create function self._set_color(self, p_color)
        2. Add pair 'color' -> self._set_color to self._tags_control in self._create_tags_control()
        3. Implement the function so that it creates xml element for color parameter and appends it to self._xml_root.
        For simple params (with one value) you can fire self._set_simple_tag('color', 'color_value').

        """
        #TODO - lapac bledy
        self.set_attributes(p_signal_params)
        self._set_remaining_tags()
        f = open(self._file_path, 'w')
        f.write(self._xml_factory.toxml('utf-8'))
        f.close()
        return self._file_path

    def _set_remaining_tags(self):
        """Set all default (hardcoded) tags and other tags as now we
        we have all needed data."""
        self.set_attributes({
                'byte_order':'LITTLE_ENDIAN',
                })

    def _create_xml_root(self):
        """Create root xml element and add standard parameters: 
        'sample_type' (double by now)
        'file' (data file`s name).
        """
        self._xml_root = self._xml_factory.createElement('OpenBciDataFormat') 
        #this is going to be an in-memory representation of xml info file
        self._xml_factory.appendChild(self._xml_root)

    def _set_tag(self, p_tag_name, p_tag_params):
        """For given tag name and tag parameters create in-memory 
        representation of xml tag. Tag type is defined in self._tags_control
        so use it to determine specific action."""
        # first get a tupe (function, list_of_function_params)
        l_ctr = self._tags_controls[p_tag_name] 
        l_std_params = list(l_ctr['params'])
        # then take list of params and append p_tag_params to it
        l_std_params.append(p_tag_params)
        
        # fire the function with all params from l_std_params
        l_ctr['function'](*l_std_params)

    def _set_simple_tag(self, p_tag_name, p_tag_value):
        """A generic method for adding an xml element with
        - tag name: 'param', 
        - id: 'p_tag_name', 
        - value: p_tag_value.
        """
        l_xml_element = self._create_xml_text_element(
            p_tag_name, types_utils.to_string(p_tag_value))
        self._xml_root.appendChild(l_xml_element)
    def _set_list_tag(
        self, p_tag_name, p_subtag_name, p_tag_values):
        """Ad xml tag like:
        <p_tag_name>
           <p_subtag_name>p_tag_values[0]</p_subtag_name>
           <p_subtag_name>p_tag_values[1]</p_subtag_name>
           ...
        </p_tag_name>
        """
        l_xml_list_root = self._xml_factory.createElement(p_tag_name)
        for i_value in p_tag_values:
            l_xml_elem = self._create_xml_text_element(
                p_subtag_name, types_utils.to_string(i_value))
            l_xml_list_root.appendChild(l_xml_elem)
        self._xml_root.appendChild(l_xml_list_root)

    def _create_xml_text_element(self, p_tag_name, p_text_value):
        """A generic method for adding an xml text element with
        - tag name: 'p_tag_name', 
        - value: p_text_value.
        - id: 'p_id_value' if different from ''
        """
        l_xml_element = self._xml_factory.createElement(p_tag_name)
        l_xml_element.appendChild(self._xml_factory.createTextNode(p_text_value))
        return l_xml_element

    def _create_tags_controls(self):
        """Define tags control functions for every recognisable parameter. 
        See self.__init__ for more details."""
        self._tags_controls = {}
        for i_tag_name, i_tag_def in TAGS_DEFINITIONS.iteritems():
            if i_tag_def[0] == 'simple':
                l_new_tag = {'function':self._set_simple_tag,
                             'params':tuple(i_tag_def[1])}
            elif i_tag_def[0] == 'list':
                l_new_tag = {'function':self._set_list_tag,
                             'params':tuple(i_tag_def[1])}
            self._tags_controls[i_tag_name] = l_new_tag
        




class GenericInfoFileReadProxy(object):
    """Info file reader."""
    def __init__(self, p_file_path):
        "..."
        self._file_path = p_file_path
        self._create_tags_control()
        self.start_reading()
    def start_reading(self):
        """Load xml to memory."""
        try:
            l_file = open(self._file_path, 'rt')
        except IOError, e:
            LOGGER.error("An error occured while opening the info file!")
            raise(e)
        else:
            try:
            #Analyse xml info file, get what we want and close the file.
                self._parse_info_file(l_file)
            except xml.parsers.expat.ExpatError, e:
                LOGGER.error("Info file is not a well-formatted xml file. \
Reading aborted!")
                raise(e)
            finally:
                l_file.close()
    def _parse_info_file(self, p_info_file):
        """Parse p_info_file xml info file and store it in memory."""
        #TODO - validate xml regarding dtd
        self._xml_doc = xml.dom.minidom.parse(p_info_file)

    def get_params(self):
        params = {}
        for key in TAGS_DEFINITIONS:
            try:
                value = self.get_param(key)
                params[key] = value
            except signal_exceptions.NoParameter:
                pass
        return params
            
    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""

        # first get a tupe (function, list_of_function_params)
        try:
            l_ctr = self._tags_controls[p_param_name] 
            l_std_params = list(l_ctr['params'])
            # fire the function with all params from l_std_params
            return l_ctr['function'](*l_std_params)
        except KeyError:
            raise(signal_exceptions.NoParameter(p_param_name))

        except IndexError:
            raise(signal_exceptions.NoParameter(p_param_name))

    def _get_simple_param(self, p_param_name):
        """Return text value from tag in format:
        <param id=p_param_name>text_value</param>."""
        LOGGER.debug("Read "+p_param_name+" tag from in-memory info xml.")
        l_name = p_param_name
        l_param = self._xml_doc.getElementsByTagName(l_name)[0]
        return l_param.firstChild.nodeValue

    def _get_list_param(self, p_param_name, p_subparam_name):
        """Return a list of text values form tag in format:
        <p_param_name>
            <param>text value1</param>
            <param>text value2</param>
            ...
        </p_param_name>
        """
        l_xml_root_element = self._xml_doc.getElementsByTagName(p_param_name)[0]
        LOGGER.debug("Will look for subtags: "+p_subparam_name+" in node: "+str(l_xml_root_element))
        l_elements = []
        for i_node in l_xml_root_element.getElementsByTagName(p_subparam_name):
            try:
                elem = i_node.firstChild.nodeValue
            except:
                LOGGER.debug("An empty node occured in tag: "+p_subparam_name)
                elem = ''
            LOGGER.debug("Found subtag node: "+str(i_node)+" with node value: "+str(elem))
            l_elements.append(elem)
        return l_elements

    def _create_tags_control(self):
        """Define tags control functions for every recognisable parameter. 
        See self.__init__ for more details."""
        self._tags_controls = {}
        for i_tag_name, i_tag_def in TAGS_DEFINITIONS.iteritems():
            if i_tag_def[0] == 'simple':
                l_new_tag = {'function':self._get_simple_param,
                             'params':tuple(i_tag_def[1])}
            elif i_tag_def[0] == 'list':
                l_new_tag = {'function':self._get_list_param,
                             'params':tuple(i_tag_def[1])}
            self._tags_controls[i_tag_name] = l_new_tag
        
