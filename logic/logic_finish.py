#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from obci.control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types

from obci.configs import settings,variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper

class LogicFinish(ConfiguredClient):
    def __init__(self, addresses):
        super(LogicFinish, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CALIBRATION)
        self.ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.text_id = int(self.config.get_param("ugm_text_id"))
        self.text = self.config.get_param("text")
        time.sleep(3)
        self.ready()

    def run(self):
        ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.text)
if __name__ == "__main__":
    LogicFinish(settings.MULTIPLEXER_ADDRESSES).run()    
    
