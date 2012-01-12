#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from multiplexer.multiplexer_constants import peers, types

#import signalml_save_manager
import sys, os.path
import settings, variables_pb2

import tags_logging as logger
from openbci.offline_analysis.obci_signal_processing.tags import tags_file_writer as tags_writer
from openbci.offline_analysis.obci_signal_processing.tags import tag_utils

from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

LOGGER = logger.get_logger("tags_saver", 'info')

TAG_FILE_EXTENSION = ".obci.tag"

class TagSaver(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        """Init slots."""
        super(TagSaver, self).__init__(addresses=addresses, 
                                          type=peers.TAG_SAVER)
        self.configure()
        # Get file path data
        l_f_name = self.config.get_param("save_file_name")
        l_f_dir = self.config.get_param("save_file_path")
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
            str_tag = variables_pb2.Tag()
            str_tag.ParseFromString(p_tag_msg)
            tag_desc = dict()
            for i_var in str_tag.desc.variables:
                tag_desc[i_var.key] = i_var.value
            l_tag = tag_utils.pack_tag_to_dict(str_tag.start_timestamp, str_tag.end_timestamp,
                                                    str_tag.name, tag_desc, str_tag.channels)

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
