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
"""Implement one class - SmartTagsManager."""
import smart_tag
from openbci.data_storage import signalml_read_manager
from openbci.data_storage import data_storage_exceptions
from openbci.offline_analysis import offline_analysis_logging as logger
import Queue
LOGGER = logger.get_logger("smart_tags_manager")

       
class SmartTagsManager(object):
    """By now manager gets in init tag definition object and dictionary of
    files paths. Regarding tag definition it iterates smart tags from file
    in iter_smart_tags().
    Public interface:
    - __init__()
    - iter_smart_tags()
    """
    def __init__(self, p_tag_def, p_files):
        """Init all needed slots, read tags file, init smart tags.
        Parameters:
        - p_tag_def - an instance of tag definition object
        (see smart_tag_definition.py)
        - p_files - a dictionary with files paths:
        'info' - info file
        'data' - data file
        'tags' - tags file
        """
        #Open files
        self._read_manager = signalml_read_manager.SignalmlReadManager(
            p_files['info'],
            p_files['data'],
            p_files['tags'])
        self._read_manager.start_reading()

        #Init slots neede to iterate smart tags properly
        self._first_sample_timestamp = float(self._read_manager.get_param(
            'first_sample_timestamp'))
        self._num_of_channels = len(self._read_manager.get_param(
            'channels_numbers'))
        l_freq_str = self._read_manager.get_param('sampling_frequency')
        self._sampling_rate = float(l_freq_str)
        self._sample_duration = 1/float(self._sampling_rate)
        self._samples_no = 0

        #Init smart tags, here just create smart tags objects without
        #data slot set.
        self._smart_tags = []
        self._init_smart_tags(p_tag_def)

    def _init_smart_tags(self, p_tag_def):
        """Init smart tags depending on given smart tag definition."""
        if p_tag_def.is_type("duration"):
            self._init_duration_smart_tags(p_tag_def)
            LOGGER.info("Finished initialising smart tags.")
        elif p_tag_def.is_type("end_tag"):
            self._init_end_tag_smart_tags(p_tag_def)
            LOGGER.info("Finished initialising smart tags.")
        else:
            LOGGER.error("Unrecognised tag definition type.")
            raise(Exception("Unrecognised tag definition type."))

    def _init_end_tag_smart_tags(self, p_tag_def):
        """Read all tags from file - create smart tags objects while doing it.
        End-tag-smart-tag is tag that begins and end with some particular tag.
        """

        l_st_queue = Queue.Queue() # Tags waiting for end tag
        while True:
            try: # Iterate over tags from file 
                i_tag = self._read_manager.get_next_tag()
            except data_storage_exceptions.NoNextTag:
                break # All tags has been red
            if i_tag['name'] in p_tag_def.end_tags_names:
                # Ending tag is met - set this tag to all smart tags waiting
                # in the queue
                while True:
                    try:
                        i_st = l_st_queue.get_nowait()
                    except:
                        break
                    i_st.set_end_tag(i_tag)
                    self._smart_tags.append(i_st)
            if i_tag['name'] == p_tag_def.start_tag_name:
                # Create new smart tag, append it to queue
                st = smart_tag.SmartTagEndTag(p_tag_def, i_tag)
                l_st_queue.put(st)

    def _init_duration_smart_tags(self, p_tag_def):
        """Read all tags from file - create smart tags objects while doing it.
        Duration-smart-tag is tag that begins with some particular tag.
        """
        while True:
            try:
                i_tag = self._read_manager.get_next_tag()
            except data_storage_exceptions.NoNextTag:
                break
            if i_tag['name'] == p_tag_def.start_tag_name:
                st = smart_tag.SmartTagDuration(p_tag_def, i_tag)
                self._smart_tags.append(st)

    def iter_smart_tags(self):
        """This is an iterator, so use id like:
        for i in mgr.iter_smart_tags():
            ....
        It iterates SmartTag objects. You can call get_data() on smart tag,
        and you will get samples for all channels for that smart tag in format:
        [[list of all samples from ch 0], [list of all samples from ch 1] ...]
        """
        for i_st in self._smart_tags:
            try:
                # First needed sample timestamp
                l_start = i_st.get_start_timestamp() 

                # Last needed sample timestamp
                l_end = i_st.get_end_timestamp() 

                LOGGER.debug("Tag start timestamp: "+str(l_start))
                LOGGER.debug("Tag end timestamp: "+str(l_end))
                if not i_st.data_empty():
                    yield i_st
                    continue
                # To-be-returned data
                l_data = [[] for i in range(self._num_of_channels)] 

                l_curr_sample_timestamp = self._get_new_curr_sample_timestamp()
                LOGGER.debug("Starting sample timestamp: "+ \
                                 str(l_curr_sample_timestamp))

                # Read samples until find first interesting sample
                while l_curr_sample_timestamp < l_start:
                    for i in range(self._num_of_channels):
                        self._read_manager.get_next_value()
                    self._samples_no = self._samples_no + 1
                    l_curr_sample_timestamp = self._get_new_curr_sample_timestamp()
                    LOGGER.debug("CURR sample timestamp: "+str(l_curr_sample_timestamp))
    
                # Now l_curr_sample_timestamp ~~ l_first
                # Store all samples until last interesting sample is met
                while l_curr_sample_timestamp < l_end:
                    for i in range(self._num_of_channels):
                        l_data[i].append(self._read_manager.get_next_value())
                    self._samples_no = self._samples_no + 1
                    l_curr_sample_timestamp = self._get_new_curr_sample_timestamp()
                    LOGGER.debug("CURR sample timestamp: "+ \
                                     str(l_curr_sample_timestamp))

                #Now l_data contains samples from all channels between
                #l_start and l_end timestamp
                i_st.set_data(l_data) # Set gathered data to smart tag
                yield i_st # Return smart tag filled with data
            except data_storage_exceptions.NoNextValue:
                LOGGER.info("No samples left. Some smart tags could have been ignored.")
                break # Exit the loop, end iterator
        self._samples_no = 0 
        #Reset samples count so that next 
        #iter_smart_tags call will work
        
    def _get_new_curr_sample_timestamp(self):
        """Return new current sample timestamp."""
        return self._first_sample_timestamp + \
            self._samples_no * self._sample_duration

    def get_sampling_rate(self):
        return self._sampling_rate

