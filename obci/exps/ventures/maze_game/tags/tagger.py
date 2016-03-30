# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#     Anna Chabuda <anna.chabuda@gmail.com>
#

from tags_file_writer import TagsFileWriter
import tag_utils
import time

import os.path

class Tagger(object):
    """docstring for Tagger"""
    def __init__(self, tag_name, tag_dir, status='ON'):
        super(Tagger, self).__init__()
        self.status = status
        self.first_timestamp = 0
        if self.status == 'ON':
            self.file_name = self._get_file_name(tag_name, tag_dir)
            self.writer = TagsFileWriter(self.file_name)
    
    # def set_first_timestamp(self, timestamp):
    #     self.first_timestamp = timestamp

    def _get_file_name(self, tag_name, tag_dir):
        return  os.path.join(tag_dir, 
                             '{}.{}.tag'.format(tag_name, 'game'))

    def set_tag(self, timestamp, tag_name, tag_value):
        if self.status == 'ON':
            tag = tag_utils.pack_tag_to_dict(timestamp, timestamp+0.1, tag_name, {'type':tag_value})
            self.writer.tag_received(tag)

    def finish(self):
        if self.status == 'ON':
            self.writer.finish_saving(self.first_timestamp)
