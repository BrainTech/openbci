#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

from configs import settings, variables_pb2

from utils import debug_helper
from acquisition import acquisition_logging as logger
LOGGER = logger.get_logger("acquisition_control", 'info')


def finish_saving():
    ctr = AcquisitionControl(settings.MULTIPLEXER_ADDRESSES)
    ctr.send_finish_saving()
    ctr.loop()
    return ctr.result


class AcquisitionControl(BaseMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(AcquisitionControl, self).__init__(addresses=addresses,
                                          type=peers.ACQUISITION_CONTROL)
        self._info_result = None
        self._data_result = None
        self._tags_result = None
        self.result = None

    def send_finish_saving(self):
        self.conn.send_message(message='finish',
                      type=types.ACQUISITION_CONTROL_MESSAGE,
                      flush=True)

    def _all_ready(self):
        return not (self._data_result is None \
                        or self._info_result is None \
                        or self._tags_result is None)

    def handle_message(self, mxmsg):
        v = variables_pb2.VariableVector()
        if mxmsg.type == types.SIGNAL_SAVER_FINISHED:
            LOGGER.info("got signal_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._data_result = v
        elif mxmsg.type == types.INFO_SAVER_FINISHED:
            LOGGER.info("got info_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._info_result = v
        elif mxmsg.type == types.TAG_SAVER_FINISHED:
            LOGGER.info("got tag_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._tags_result = v
        else:
            LOGGER.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.result = self._info_result, self._data_result, self._tags_result
            LOGGER.info(''.join(["Stop acquisition_control with result: ", "\n",
                                 "info result:\n",
                                 debug_helper.get_str_variable_vector(self._info_result),
                                 "data result:\n",
                                 debug_helper.get_str_variable_vector(self._data_result),
                                 "tagsd result:\n",
                                 debug_helper.get_str_variable_vector(self._tags_result)
                                 ])
                        )
            self.working = False

