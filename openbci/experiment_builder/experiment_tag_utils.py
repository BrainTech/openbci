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
# Utilities for 'experiment_update' tag handling.
#"""
from tags.tag_utils import unpack_tag_from_dict 

def unpack_upd_exp_tag(p_tag):
    """
    Unpack tag using tag_utils and then convert experiment_update specific
    values from strings to proper data types.
    #TODO use fancy tag definitions
    """
    utag = unpack_tag_from_dict(p_tag)
    if utag['name'] != 'experiment_update':
        return p_tag
    params = utag['desc']['desc']
    f_str = params['Freqs']
    if not hasattr(f_str, 'split'):
        # already unpacked, f_str not a string
        return utag
    # process freqs list in string format
    f_str = f_str[1:-1].split(', ')
    t_freqs = [float(f) for f in f_str]
    params['Freqs'] = t_freqs
    # field number originally counted from 1
    field_no = int(params['concentrating_on_field']) - 1
    params['concentrating_on_field'] = field_no
    delay = int(params['delay'])
    params['delay'] = delay      
    if params.has_key('break'):
        br = bool(params['break'])
        params['break'] = br
        
    return utag  

def basic_params(p_unpacked_tag):
    """
    Return freqs, concentrating_on_field, delay from 'experiment_update' tag.
    """
    params = p_unpacked_tag['desc']['desc']
    t_freqs = params['Freqs']
    field_no = params['concentrating_on_field']
    delay = params['delay']
    return t_freqs, field_no, delay

