#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path, sys, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings, variables_pb2
from gui.ugm import ugm_config_manager
from gui.ugm import ugm_helper
from utils import keystroke
from acquisition import acquisition_helper

from logic import logic_logging as logger
LOGGER = logger.get_logger("logic_p300_calibration", "info")

class LogicP300Calibration(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicP300Calibration, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CALIBRATION)
        self.blinking_ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.hi_text = self.config.get_param("hi_text")
        self.bye_text = self.config.get_param("bye_text")
        self.break_text = self.config.get_param("break_text")
        self.break_duration = float(self.config.get_param("break_duration"))
        self.trials_count = int(self.config.get_param("trials_count"))

        self._trials_counter = self.trials_count
        self.ready()
        self.begin()
        
    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys decision to logic engine."""
        if (mxmsg.type == types.UGM_ENGINE_MESSAGE):
            msg = variables_pb2.Variable()
            msg.ParseFromString(mxmsg.message)
            if msg.key == "blinking_stopped":
                LOGGER.info("Got blinking stopped message!")
                self._trials_counter -= 1
                if self._trials_counter <= 0:
                    LOGGER.info("All trials passed")
                    self.end()
                else:
                    LOGGER.info("Blinking stopped...")
                    self.blinking_stopped()
            else:
                LOGGER.info("Got unrecognised ugm engine message: "+str(msg.key))
        else:
            LOGGER.warning("Got unrecognised message type: "+mxmsg.type)
        self.no_response()

    def begin(self):
        ugm_helper.send_text(self.conn, self.hi_text)
        keystroke.wait([" "])
        LOGGER.info("Send begin config ...")
        ugm_helper.send_config(self.conn, self.blinking_ugm)
        LOGGER.info("Send start blinking on begin ...")
        ugm_helper.send_start_blinking(self.conn)

    def end(self):
        ugm_helper.send_text(self.conn, self.bye_text)
        acquisition_helper.send_finish_saving(self.conn)
    
    def blinking_stopped(self):
        ugm_helper.send_text(self.conn, self.break_text)
        time.sleep(self.break_duration)
        ugm_helper.send_config(self.conn, self.blinking_ugm)
        ugm_helper.send_start_blinking(self.conn)

if __name__ == "__main__":
    LogicP300Calibration(settings.MULTIPLEXER_ADDRESSES).loop()
