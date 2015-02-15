#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

from obci.configs import settings, variables_pb2

from obci.utils import debug_helper

from obci.acquisition import acquisition_logging as logger
LOGGER = logger.get_logger("acquisition_control", 'info')


def finish_saving(mx_addresses=settings.MULTIPLEXER_ADDRESSES, s_types=['eeg']):
    ctr = AcquisitionControl(mx_addresses, s_types)
    ctr.send_finish_saving()
    ctr.loop()
    return ctr.result

def wait_saving_finished(mx_addresses=settings.MULTIPLEXER_ADDRESSES, s_types=['eeg']):
    ctr = AcquisitionControl(mx_addresses, s_types)
    ctr.loop()
    return ctr.result


class AcquisitionControl(BaseMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses, s_types=['eeg']):
        super(AcquisitionControl, self).__init__(addresses=addresses,
                                          type=peers.ACQUISITION_CONTROL)
        self._info_result = None
        self._data_result = None
        self._tags_result = None
        self._wii_info_result = None
        self._wii_data_result = None
        self._wii_tags_result = None

        self._wii_type = 'wii' in s_types
        self._eeg_type = 'eeg' in s_types
        assert(self._wii_type or self._eeg_type)

        self.result = None

    def send_finish_saving(self):
        self.conn.send_message(message='finish',
                      type=types.ACQUISITION_CONTROL_MESSAGE,
                      flush=True)

    def _all_ready(self):
        eeg_ready = not (self._data_result is None  or self._info_result is None or self._tags_result is None)
        wii_ready = not (self._wii_data_result is None  or self._wii_info_result is None or self._wii_tags_result is None)
        if self._wii_type and self._eeg_type:
            return eeg_ready and wii_ready
        elif self._wii_type:
            return wii_ready
        elif self._eeg_type:
            return eeg_ready
        else:
            raise Exception ("no wii or eeg signal type detecetd")
            

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
        elif mxmsg.type == types.WII_BOARD_SIGNAL_SAVER_FINISHED:
            LOGGER.info("got wii signal_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._wii_data_result = v
        elif mxmsg.type == types.WII_BOARD_INFO_SAVER_FINISHED:
            LOGGER.info("got wii info_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._wii_info_result = v
        elif mxmsg.type == types.WII_BOARD_TAG_SAVER_FINISHED:
            LOGGER.info("got wii tag_saver_finished")
            v.ParseFromString(mxmsg.message)
            self._wii_tags_result = v
        else:
            LOGGER.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.result = self._info_result, self._data_result, self._tags_result, self._wii_info_result, self._wii_data_result, self._wii_tags_result
            LOGGER.info(''.join(["Stop acquisition_control with result: ", "\n"]))
            if self._eeg_type:
                LOGGER.info(''.join([ "info result:\n",
                                 debug_helper.get_str_variable_vector(self._info_result),
                                 "data result:\n",
                                 debug_helper.get_str_variable_vector(self._data_result),
                                 "tags result:\n",
                                 debug_helper.get_str_variable_vector(self._tags_result)
                                 ]))
            if self._wii_type:
                LOGGER.info(''.join([ "\n wii info result:\n",
                                 debug_helper.get_str_variable_vector(self._wii_info_result),
                                 "wii data result:\n",
                                 debug_helper.get_str_variable_vector(self._wii_data_result),
                                 "wii tags result:\n",
                                 debug_helper.get_str_variable_vector(self._wii_tags_result)
                                 ]))
            self.working = False

