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


from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

#import signalml_save_manager
import sys, time, os.path
import settings, variables_pb2

import tags_logging as logger
import tagger
from openbci.offline_analysis.obci_signal_processing.tags import tags_file_writer as tags_writer

LOGGER = logger.get_logger("tags_saver", 'info')
TAGGER = tagger.get_tagger()

TAG_FILE_EXTENSION = ".obci.tag"

class TagSaver(BaseMultiplexerServer):
    def __init__(self, addresses):
        """Init slots."""
        super(TagSaver, self).__init__(addresses=addresses, 
                                          type=peers.TAG_SAVER)

        # Get file path data from hashtable...
        l_f_name =  self.conn.query(message = "SaveFileName", 
                                    type = types.DICT_GET_REQUEST_MESSAGE, 
                                    timeout = 1).message
        l_f_dir = self.conn.query(message = "SaveFilePath", 
                                   type = types.DICT_GET_REQUEST_MESSAGE, 
                                   timeout = 1).message

        l_file_path = os.path.normpath(os.path.join(
               l_f_dir, l_f_name + TAG_FILE_EXTENSION))


        self._tags_proxy = tags_writer.TagsFileWriter(l_file_path)
        self._session_is_active = True

    def handle_message(self, mxmsg):
        """Handle messages:
        * Tag message - raw data from mx (TAG)
        If session is active convey data to save_manager.
        * signal_saver_control_message - a message from signal saver
        is a signal to finishing saving tags.
        depending on data received."""
        if mxmsg.type == types.TAG and \
                self._session_is_active:
            l_tag = TAGGER.unpack_tag(mxmsg.message) #TOOD - dont use tagger, use tag_utils
            LOGGER.info(''.join(['Signal saver got tag: ',
                                'start_timestamp:',
                                str(l_tag['start_timestamp']),
                                ', end_timestamp: ', 
                                str(l_tag['end_timestamp']),
                                ', name: ',
                                l_tag['name'],
                                '. <Change debug level to see desc.>']))
                                  
            LOGGER.debug("Signal saver got tag: "+str(l_tag))
            self._tag_received(l_tag)

        elif mxmsg.type == types.SIGNAL_SAVER_CONTROL_MESSAGE:

            l_vec = variables_pb2.VariableVector()
            l_vec.ParseFromString(mxmsg.message)
            for i_var in l_vec.variables:
                # Assume that first_sample_timestamp key is
                # in a dictinary got from signal saver
                if i_var.key == 'first_sample_timestamp':
                    self._finish_saving(float(i_var.value))
                    break

    def _finish_saving(self, p_first_sample_ts):
        """Save all tags to xml file, but first update their 
        .position field so that it is relative to timestamp
        of a first sample stored by signal saver (p_first_sample_ts)."""

        if not self._session_is_active:
            LOGGER.error("Attempting to finish saving tags while session is not active.!")
            return 
        self._session_is_active = False

        # Save tags
        l_file_path = self._tags_proxy.finish_saving(p_first_sample_ts)
        LOGGER.info("Tags file saved to: "+l_file_path)
        return l_file_path

    def _tag_received(self, p_tag_dict):
        """Convey tag to tags_proxy."""
        self._tags_proxy.tag_received(p_tag_dict)



if __name__ == "__main__":
    TagSaver(settings.MULTIPLEXER_ADDRESSES).loop()
