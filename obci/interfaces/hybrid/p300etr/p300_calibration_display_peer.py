#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helps analyse data and sends it to decision making module.

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

import os.path, sys, time

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper
from obci.utils import keystroke
from obci.utils import tags_helper

from obci.acquisition import acquisition_helper
from obci.utils.openbci_logging import log_crash

class LogicP300Calibration(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(LogicP300Calibration, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CALIBRATION)
        self.blinking_ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.hi_text = self.config.get_param("hi_text")
        self.bye_text = self.config.get_param("bye_text")
        self.break_text = self.config.get_param("break_text")
        self.break_duration = float(self.config.get_param("break_duration"))
        self.trials_count = int(self.config.get_param("trials_count"))
        #~ self.current_target = int(self.config.get_param("target"))
        self.current_target = [int(x) for x in self.config.get_param("target").split(';')]

        self.blink_duration = float(self.config.get_param("blink_duration"))

        self._trials_counter = self.trials_count
        self.ready()
        self.begin()
        
    def handle_message(self, mxmsg):
        """Method fired by multiplexer. It conveys decision to logic engine."""
        if (mxmsg.type == types.UGM_ENGINE_MESSAGE):
            self._handle_ugm_engine(mxmsg.message)
        elif mxmsg.type == types.BLINK_MESSAGE:
            self._handle_blink(mxmsg.message)
        else:
            self.logger.warning("Got unrecognised message type: "+mxmsg.type)
        self.no_response()

    def _handle_blink(self, msg):
        b = variables_pb2.Blink()
        b.ParseFromString(msg)
        self.logger.debug("GOT BLINK: "+str(b.timestamp)+" / "+str(b.index))
        tags_helper.send_tag(self.conn, 
                             b.timestamp, b.timestamp+self.blink_duration, "blink",
                             {"index" : b.index,
                              "target":self.current_target
                              })

    def _handle_ugm_engine(self, msg):
        m = variables_pb2.Variable()
        m.ParseFromString(msg)
        if m.key == "blinking_stopped":
            self.logger.info("Got blinking stopped message!")
            self._trials_counter -= 1
            if self._trials_counter <= 0:
                self.logger.info("All trials passed")
                self.end()
            else:
                self.logger.info("Blinking stopped...")
                self.blinking_stopped()
        else:
            self.logger.info("Got unrecognised ugm engine message: "+str(m.key))

    def begin(self):
        ugm_helper.send_text(self.conn, self.hi_text)
        #keystroke.wait([" "])
        time.sleep(5)
        self.logger.info("Send begin config ...")
        ugm_helper.send_config(self.conn, self.blinking_ugm)
        self.logger.info("Send start blinking on begin ...")
        ugm_helper.send_start_blinking(self.conn)

    def end(self):
        ugm_helper.send_text(self.conn, self.bye_text)
        #acquire some more data
        time.sleep(2)
        acquisition_helper.send_finish_saving(self.conn)
    
    def blinking_stopped(self):
        time.sleep(1)
        ugm_helper.send_text(self.conn, self.break_text)
        time.sleep(self.break_duration)
        ugm_helper.send_config(self.conn, self.blinking_ugm)
        time.sleep(1)
        ugm_helper.send_start_blinking(self.conn)

if __name__ == "__main__":
    LogicP300Calibration(settings.MULTIPLEXER_ADDRESSES).loop()
