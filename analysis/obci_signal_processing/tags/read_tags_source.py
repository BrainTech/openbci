# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import copy
import tags_file_reader
import tags_logging as logger
LOGGER = logger.get_logger("smart_tags_source", "info")


class TagsSource(object):
    def get_tags(self):
        LOGGER.error("The method must be subclassed")

    def _filter_tags(self, p_tags, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        l_tags = p_tags
        if not (p_tag_type is None):
            l_tags = [i_tag for i_tag in l_tags if p_tag_type == i_tag['name']]

        if not (p_from is None):
            l_start = p_from
            l_end = p_from + p_len
            l_tags = [i_tag for i_tag in l_tags if 
                      (l_start <= i_tag['start_timestamp'] and i_tag['start_timestamp'] <= l_end)]

        if not (p_func is None):
            l_tags = [i_tag for i_tag in l_tags if p_func(i_tag)]

        return l_tags
    def __deepcopy__(self, memo):
        return MemoryTagsSource(copy.deepcopy(self.get_tags()))

class MemoryTagsSource(TagsSource):
    def __init__(self, p_tags = None):
        self._tags = None
        if not (p_tags is None):
            self.set_tags(p_tags)
    def set_tags(self, p_tags):
        self._tags = p_tags

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        return self._filter_tags(
            self._tags,
            p_tag_type, p_from, p_len, p_func)
    


class FileTagsSource(TagsSource):
    def __init__(self, p_file_path):
        self._memory_source = None
        self._tags_proxy = tags_file_reader.TagsFileReader(p_file_path)

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        if self._memory_source is None:
            return self._filter_tags(
                self._tags_proxy.get_tags(),
                p_tag_type, p_from, p_len, p_func)
        else:
            self._memory_source.get_tags(p_tag_type, p_from, p_len, p_func)

    def set_tags(self, p_tags):
        if self._memory_source is None:
            self._memory_source = MemoryTagsSource(p_tags)
        else:
            self._memory_source.set_tags(p_tags)
        
