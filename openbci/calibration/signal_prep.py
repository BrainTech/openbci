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
#      Joanna Tustanowska <asia.tustanowska@gmail.com>
#
#"""
# Preparing signal data for analysis.
#"""

import experiment_builder.experiment_tag_utils as exp_utils
from openbci.offline_analysis import smart_tags_manager as tag_mgr
from openbci.offline_analysis import smart_tag_definition as tag_df  

class SignalPrep(object):
    """
    Abstract class for slicing experiment signal data to be used during calibration.
    For future enhancements.
    """
    def __init__(self, **params):
        pass
    
#    def unpack_upd_exp_tag(self, p_tag):
#        """
#        Unpack tag using tag_utils and then convert experiment_update specific
#        values from strings to proper data types.
#        #TODO use fancy tag definitions
#        """
#        utag = unpack_tag_from_dict(p_tag)
#        if utag['name'] != 'experiment_update':
#            return p_tag
#        params = utag['desc']['desc']
#        f_str = params['Freqs']
#        # process freqs list in string format
#        f_str = f_str[1:-1].split(', ')
#        t_freqs = [float(f) for f in f_str]
#        params['Freqs'] = t_freqs
#        # field number originally counted from 1
#        field_no = int(params['concentrating_on_field']) - 1
#        params['concentrating_on_field'] = field_no
#        delay = int(params['delay'])
#        params['delay'] = delay      
#        if params.has_key('break'):
#            br = bool(params['break'])
#            params['break'] = br
#            
#        return utag  
#    
#    def basic_params(self, p_unpacked_tag):
#        params = p_unpacked_tag['desc']['desc']
#        t_freqs = params['Freqs']
#        field_no = params['concentrating_on_field']
#        delay = params['delay']
#        return t_freqs, field_no, delay
    
    def get_sampling_rate(self):
        """
        Return sampling rate of the signal.
        """
        pass
    
    def iter_nonbreak_slices(self, chan_no):
        pass
        
    def iter_all_exp_slices(self, chan_no):
        pass


class OfflineSignalPrep(SignalPrep):
    """
    Slice signal data written to obci file.
    Interface:
        - iter_all_exp_slices(chan_number)
        - iter_nonbreak_slices(chan_number)
    """
    def __init__(self, **params):
        """
        Mandatory:
        base_file_name - so the real file names are like: base_file_name.obci.*
        dir_path - path to signal files directory
        """
        super(OfflineSignalPrep, self).__init__(**params)
        if not params.has_key('base_file_name') or \
             not params.has_key('dir_path'):
            raise Exception("Path and name of signal files required!")
            
        self._base_file_name = params['base_file_name']
        self._dir_path = params['dir_path']
        print self._dir_path, "  ", self._base_file_name
        self._files = {'info': self._dir_path + '/' +self._base_file_name + '.obci.info',
             'data': self._dir_path + '/' +self._base_file_name + '.obci.dat',
             'tags': self._dir_path + '/' +self._base_file_name + '.obci.tags'
                }

        tags_def = tag_df.SmartTagEndTagDefinition(
                start_tag_name='experiment_update',
                start_offset=0, end_offset=0,
                end_tags_names=['experiment_update', 'experiment_end'])

        
        self._tag_manager = tag_mgr.SmartTagsManager(tags_def, self._files)
    
    def iter_nonbreak_slices(self, chan_no):
        """
        Iterate slices of signal data + start tags, which aren't experiment breaks.
        chan_no - signal channel number
        """
        for t in self._tag_manager.iter_smart_tags():
            start = t.get_start_tag()
            if start['name'] == 'experiment_update':
                if start['desc'].has_key('break'):
                    continue
                else:
                    yield t.get_data()[chan_no], exp_utils.unpack_upd_exp_tag(start)
            
    def iter_all_exp_slices(self, chan_no):
        """
        Iterate all slices of data and their start tags.
        chan_no - signal channel number
        """
        
        for t in self._tag_manager.iter_smart_tags():
            start = t.get_start_tag()
            if start['name'] == 'experiment_update':
                yield t.get_data()[chan_no], exp_utils.unpack_upd_exp_tag(start)
                
    def get_sampling_rate(self):
        """
        Return sampling rate of the signal.
        """
        return self._tag_manager.get_sampling_rate()
    
    