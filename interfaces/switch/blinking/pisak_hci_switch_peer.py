#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from obci.gui.ugm import ugm_helper

import random, time, sys

class HciSwitch(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(HciSwitch, self).__init__(addresses=addresses,
                                        type=peers.SWITCH_ANALYSIS)
        self._curr_index = -1
        self._last_dec_time = time.time()
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        ######
        self.ugm_rows = int(self.config.get_param('blink_ugm_row_count'))
        self.ugm_columns = int(self.config.get_param('blink_ugm_col_count'))
        self.ugm_blink_type = self.config.get_param('blink_ugm_type')
        self.ugm_fields_each_row = self.config.get_param('blink_ugm_fields_row_count').split(';')
        self.ugm_blink_count = 0
        self.ugm_cycle_count = 2
        self.ugm_current_row = 0
        ######
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.BLINK_MESSAGE:
            l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.logger.debug("Got blink message: "+str(l_msg.index))
            self._curr_index = int(l_msg.index)

            if self.ugm_blink_type == 'single':
                self.ugm_blink_count += 1
                if self.ugm_blink_count >= self.ugm_cycle_count*int(self.ugm_fields_each_row[self.ugm_current_row]):
                    self.logger.info("Passed "+str(self.ugm_cycle_count)+" cycles, change blinking to single")
                    self.ugm_blink_type = 'classic'
                    ugm_helper.send_update_and_start_blinking(self.conn, str({'blink_id_start':self.ugm_columns, 'blink_id_count':self.ugm_rows, 'blink_ugm_type':self.ugm_blink_type}))
                    self.ugm_blink_count = 0

        elif mxmsg.type == types.SWITCH_MESSAGE:
        #process blinks only when hold_time passed
            if self._last_dec_time > 0:
                t = time.time() - self._last_dec_time
                if t > self.hold_after_dec:
                    self._last_dec_time = 0
                else:
                    self.no_response()
                    return
            if self._curr_index < 0:
                self.logger.warning("Got switch message, but curr_index < 0. Do nothing!!!")

            elif self.ugm_blink_type == 'classic':
                self.logger.info("Got switch message, change blinking to single")
                self.ugm_blink_type = 'single'
                self.ugm_current_row = self._curr_index - self.ugm_columns
                ugm_helper.send_update_and_start_blinking(self.conn, str({'blink_id_start':(self._curr_index - self.ugm_columns)*self.ugm_columns, 'blink_id_count':self.ugm_fields_each_row[self.ugm_current_row], 'blink_ugm_type':self.ugm_blink_type}))

            else:
                self.logger.info("Got switch message, send curr index == "+str(self._curr_index))
                self._last_dec_time = time.time()
                self.ugm_blink_type = 'classic'
                ugm_helper.send_update_and_start_blinking(self.conn, str({'blink_id_start':self.ugm_columns, 'blink_id_count':self.ugm_rows, 'blink_ugm_type':self.ugm_blink_type}))
                self.ugm_blink_count = 0
                self.conn.send_message(message = str(self._curr_index),
                                       type = types.DECISION_MESSAGE, flush=True)
        else:
            self.logger.warning("Got unrecognised message: "+str(mxmsg.type))
        self.no_response()

if __name__ == "__main__":
    HciSwitch(settings.MULTIPLEXER_ADDRESSES).loop()
