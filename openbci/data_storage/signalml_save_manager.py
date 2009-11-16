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

import sys, os.path, struct

import xml.dom.minidom

data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"

class BadSampleFormat(Exception):
    """An exception that should be raised when data sample has arrived and it is not float (struct is unable to pack it)."""
    def __str__(self):
        return "Error! Received data sample is not of 'float' type! Writing to file aborted!"

class InfoFileProxy(object):
    """A class that is responsible for implementing logics of openbci signal parameters storage in info file.
    The file is supposed to be compatible with signalml2.0. By now it isn`t:)
    The class should be separated from all multiplexer-stuff logics.
    InfoFileProxy represents a process of saving one signal parameters.
    Init method gets a dictionary of signal params in format understadable by InfoFileProxy. See __init__ metod for more details.
    Wanna extend info file with a new param? See __init__ method for more details.
    Public interface:
    - finish_saving()
    """
    def __init__(self, p_file_name, p_dir_path, p_signal_params):
        """
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
        For simple params (with one value) you can fire self._set_simple_param_tag('color', 'color_value').
        """
        self._file_name = os.path.normpath(os.path.join(p_dir_path, p_file_name + info_file_extension)) 
        #TODO works in windows and linux on path with spaces?
        self._xml_factory = xml.dom.minidom.Document() #an object useful in the future to easily create xml elements
        self._create_xml_root(p_file_name)
        self._create_tags_controls()
        self._process_signal_params(p_signal_params)

    def finish_saving(self, p_samples_count):
        """Write xml_doc to the file, return the file`s path."""
        #TODO - lapac bledy
        self._set_tag('number_of_samples', p_samples_count)
        f = open(self._file_name, 'w')
        f.write(self._xml_factory.toxml('utf-8')) #TODO ustawic kodowanie
        f.close()
        return self._file_name

    def _create_xml_root(self, p_file_name):
        """Create root xml element and add standard parameters: 
        'sample_type' (double by now)
        'file' (data file`s name).
        """
        self._xml_root = self._xml_factory.createElement('openbci_signal_data_format') #this is going to be an in-memory representation of xml info file
        self._xml_factory.appendChild(self._xml_root)
        l_file_element = self._create_xml_text_element('file', p_file_name + data_file_extension)
        l_sample_type_element = self._create_xml_text_element('param', 'double', 'sample_type')
        
        self._xml_root.appendChild(l_file_element)
        self._xml_root.appendChild(l_sample_type_element)
        

    def _process_signal_params(self, p_signal_params):
        """Fire _set_tag for every key->value pair in p_signal_params. See self.__init__ doctring to learn about p_signal_params.""" 
        for i_param_name, i_param_values in p_signal_params.iteritems():
            self._set_tag(i_param_name, i_param_values)
        pass
    def _set_tag(self, p_tag_name, p_tag_params):
        self._tags_controls[p_tag_name](p_tag_params)


    #Setter methods for every recogisable signal parameter ********************************************************************
    def _set_channels_names(self, p_channels_names):
        """Create xml element for 'channels_names' parameter. 
        p_channels_names should be a list of channel names."""
        l_xml_channel_root = self._xml_factory.createElement('channels_names')
        for i_channel_name in p_channels_names:
            l_channel_xml = self._create_xml_text_element('param', i_channel_name, 'channel_name')
            l_xml_channel_root.appendChild(l_channel_xml)
        self._xml_root.appendChild(l_xml_channel_root)

    def _set_number_of_samples(self, p_samples_count):
        """Create xml element for 'number_of_samples' parameter. 
        p_samples_count should be a number of samples."""
        self._set_simple_param_tag('number_of_samples', str(p_samples_count))

    def _set_number_of_channels(self, p_channels_count):
        """Create xml element for 'number_of_channels' parameter. 
        p_channels_count should be a number of channels."""
        self._set_simple_param_tag('number_of_channels', str(p_channels_count))
        
    def _set_sampling_frequency(self, p_sampling):
        """Create xml element for 'sampling_frequency' parameter. 
        p_sampling should be a number representing sampling fraequency."""
        self._set_simple_param_tag('sampling_frequency', str(p_sampling))
    #Setter methods for every recogisable signal parameter ********************************************************************

    def _set_simple_param_tag(self, p_tag_id, p_tag_value):
        """A generic method for adding an xml element with
        - tag name: 'param', 
        - id: 'p_tag_id', 
        - value: p_tag_value.
        """
        l_xml_element = self._create_xml_text_element('param', p_tag_value, p_tag_id)
        self._xml_root.appendChild(l_xml_element)
        
    def _create_xml_text_element(self, p_tag_name, p_text_value, p_id_value=''):
        """A generic method for adding an xml text element with
        - tag name: 'p_tag_name', 
        - value: p_text_value.
        - id: 'p_id_value' if different from ''
        """
        l_xml_element = self._xml_factory.createElement(p_tag_name)
        l_xml_element.appendChild(self._xml_factory.createTextNode(p_text_value))
        if p_id_value != '':
            l_xml_element.setAttribute('id', p_id_value)
        return l_xml_element
    def _create_tags_controls(self):
        """Define tags control functions for every recognisable parameter. See self.__init__ for more details."""
        self._tags_controls = {
            'channels_names':self._set_channels_names,
            'number_of_samples':self._set_number_of_samples,
            'number_of_channels':self._set_number_of_channels,
            'sampling_frequency': self._set_sampling_frequency
            }
        

class DataFileProxy(object):
    """
    A class representing data file. 
    It should be an abstraction for saving raw data into a file. 
    Decision whether save signal to one or few separate files should be made here 
    and should be transparent regarding below interface - the interface should remain untouched.
    Public interface:
    - finish_saving() - closes data file and return its path,
    - data_received(p_data_sample) - gets and saves next sample of signal
    """
    def __init__(self, p_file_name, p_dir_path):
        """Open p_file_name file in p_dir_path directory."""
        self._number_of_samples = 0
        self._file_name = os.path.normpath(os.path.join(p_dir_path, p_file_name + data_file_extension))
        #TODO works in windows and linux on path with spaces?
        try:
            #TODO - co jesli plik istnieje?
            self._file = open(self._file_name, 'wr') #open file in a binary mode
        except IOError:
            print "Error! Can`t create a file!!!."
            sys.exit(1)

    def finish_saving(self):
        """Close the file, return a tuple - file`s name and number of samples."""
        self._file.close()
        return self._file_name, self._number_of_samples

    def data_received(self, p_data):
        """ Write p_data t self._file as raw int. Here we assume, that
        p_data is of float type. Type verification should be conducted earlier."""
        try:
            self._file.write(struct.pack("d", p_data)) 
        except ValueError:
            print("Warning! Trying to write data to closed data file!")
            return
        except struct.error:
            raise(BadSampleFormat())
            
        self._file.flush()
        #store number of samples
        self._number_of_samples = self._number_of_samples + 1



class SignalmlSaveManager(object):
    """A class that is responsible for implementing logics of openbci signal stroing
    eg. what goes to which files, what kind of files are to be created etc.
    The class should be separated from all multiplexer-stuff logics.
    SaverObject represents a process of saving one signal.
    Public interface:
    - finish_saving()
    - data_received(p_data_sample)
    """
    def __init__(self, p_session_name, p_dir_path, p_signal_params):
        """
        Init data file and info file proxies representing saving process.
        Arguments:
        p_session_name - a name of file(s) to be created
        p_dir_path - a path to dir where files are to be created
        p_signal_params- a dictionary of signal parameters like number of channels etc, 
        params should be readablye by InfoFileProxy, see its __init__ method t learn more.
        """
        self._info_proxy = InfoFileProxy(p_session_name, p_dir_path, p_signal_params)
        self._data_proxy = DataFileProxy(p_session_name, p_dir_path)
        #TODO co z tagami? trzeba by tutaj chyba dostarczac jakiś obiekt, ktory takie tagi rozumie, hmmm, ale też chyba SignamlSignalSaver musi takie tagi rozmiec...
        #na razie przyjmiemy że tagów nie ma

    def finish_saving(self):
        """ Return a tuple x,y where:
        x - canonised path to info file
        y - canonised path to data file
        """
        #TODO - sprawdzanie bledow
        l_data_file_path, l_samples_count = self._data_proxy.finish_saving()
        l_info_file_path = self._info_proxy.finish_saving(l_samples_count)
        return l_info_file_path, l_data_file_path


    def data_received(self, p_data):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy."""
        try:
            self._data_proxy.data_received(p_data)
        except BadSampleFormat, e:
            print(e)
            sys.exit(1)
            
