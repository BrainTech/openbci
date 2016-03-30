# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import sys, struct, time, numpy, copy, os.path

from signal import read_data_source
from signal import read_info_source
from tags import read_tags_source

from signal import data_raw_write_proxy
from signal import info_file_proxy
from tags import tags_file_writer

import obci_signal_processing_logging as logger
LOGGER = logger.get_logger("read_manager", "info")

class ReadManager(object):
    """A class responsible for reding openbci file format.
    Public interface:
    - start_reading() - open info and data file,
    - get_next_value() - get next value from data file,
    - get_param(param_name) - get param_name parameter from info file.

    Wanna be able to read a new parameter 'new_param'?
    1. Register reading function in self._create_info_tags_control() under 'new_param' key.
    2. Implement the function (it should be considered as class private function, not callable from outside; 
    the function should return a value for 'new_param' request).
    3. Call get_param('new_param') every time you want to get the param.
    """
    def __init__(self, p_info_source, p_data_source, p_tags_source):
        """Just remember info file path and data file path."""
        try:
            ''+p_info_source
            LOGGER.debug("Got info source file path.")
            self.info_source = read_info_source.FileInfoSource(p_info_source)
        except TypeError:
            LOGGER.debug("Got info source object.")
            self.info_source = p_info_source

        try:
            ''+p_data_source
            LOGGER.debug("Got data source file path.")
            self.data_source = read_data_source.FileDataSource(
                p_data_source,
                int(self.info_source.get_param('number_of_channels')),
                self.info_source.get_param('sample_type')
                )
        except TypeError:
            LOGGER.debug("Got data source object.")
            self.data_source = p_data_source

        try:
            ''+p_tags_source
            LOGGER.debug("Got tags source file path.")
            self.tags_source = read_tags_source.FileTagsSource(p_tags_source)
        except TypeError:
            LOGGER.debug("Got tags source object.")
            self.tags_source = p_tags_source 

    def __deepcopy__(self, memo):
        info_source = copy.deepcopy(self.info_source)
        tags_source = copy.deepcopy(self.tags_source)
        samples_source = copy.deepcopy(self.data_source)
        return ReadManager(info_source, samples_source, tags_source)

    def save_to_file(self, p_dir, p_name):
        tags = self.get_tags()
        params = self.get_params()

        path = os.path.join(p_dir, p_name)
        #store tags
        tags_writer = tags_file_writer.TagsFileWriter(path+'.obci.tag')
        for tag in tags:
            tags_writer.tag_received(tag)

        #store info
        info_writer = info_file_proxy.InfoFileWriteProxy(path+'.obci.xml')
        info_writer.set_attributes(params)

        #store data
        data_writer = data_raw_write_proxy.DataRawWriteProxy(path+'.obci.raw')
        for sample in self.iter_samples():
            for d in sample:
                data_writer.data_received(d)

        tags_writer.finish_saving(0)        
        info_writer.finish_saving()
        data_writer.finish_saving()


    def get_samples(self, p_from=None, p_len=None, p_unit='sample'):
        """Return a two dimensional array of signal values.
        if p_reload then refresh the file, otherwise use cached values.
        p_unit can be 'sample' or 'second' and makes sense only if p_from and p_len is not none."""
        if p_unit == 'sample':
            return self.data_source.get_samples(p_from, p_len)
        elif p_unit == 'second':
            sampling = int(float(self.get_param('sampling_frequency')))
            return self.data_source.get_samples(p_from*sampling, p_len*sampling)
        else:
            raise Exception('Unrecognised unit type. Should be sample or second!. Abort!')
        

    def get_channel_samples(self, p_ch_name, p_from=None, p_len=None, p_unit='sample'):
        """Return an array of values for channel p_ch_name, or
        raise ValueError exception if there is channel with that name.
        p_unit can be 'sample' or 'second' and makes sense only if p_from and p_len is not none."""

        ch_ind = self.get_param('channels_names').index(p_ch_name) #TODO error
        return self.get_samples(p_from, p_len, p_unit)[ch_ind]
        
    def get_channels_samples(self, p_ch_names, p_from=None, p_len=None, p_unit='sample'):
	assert(len(p_ch_names) > 0)
        s = self.get_channel_samples(p_ch_names[0], p_from, p_len, p_unit)
        for ch in p_ch_names[1:]:
            s = numpy.vstack((s, self.get_channel_samples(ch, p_from, p_len, p_unit))) 
        return s

    def set_samples(self, p_samples, p_channel_names, p_copy=False):
        try:
            dim = p_samples.ndim
        except AttributeError:
            raise Exception("Samples not a numpy array!")
        if (dim != 2):
            raise Exception("Samples must be a 2-dim numpy array!")
        num_of_channels = p_samples.shape[0]
        num_of_samples = p_samples.shape[1]
        
        if (len(p_channel_names) != num_of_channels):
            raise Exception("Number of channels names is different from number of channels in samples!")
        
        self.set_param('channels_names', p_channel_names)
        self.set_param('number_of_channels', num_of_channels)
        self.set_param('number_of_samples', num_of_samples)
        self.data_source.set_samples(p_samples, p_copy)


    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """Return all tags of type tag_type, or all types if tag_type is None."""

        if self.tags_source is None:
            return []
        else:
            return self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func)
    def set_tags(self, p_tags):
        if self.tags_source is not None:
            self.tags_source.set_tags(p_tags)
        else:
            self.tags_source = read_tags_source.MemoryTagsSource(p_tags)

    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""
        return self.info_source.get_param(p_param_name)

    def get_params(self):
        return self.info_source.get_params()

    def set_param(self, p_key, p_value):
        self.info_source.set_param(p_key, p_value)

    def set_params(self, p_params):
        self.info_source.update_params(p_params)

    def reset_params(self):
        self.info_source.reset_params()

    def iter_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        if self.tags_source is None:
            return 

        for tag in self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func):
            yield tag
        
    def iter_samples(self):
        for s in self.data_source.iter_samples():
            yield s
            
