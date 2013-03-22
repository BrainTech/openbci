#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from obci.control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types
from obci.utils import context as ctx
from obci.configs import settings,variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper

class LogicFinish(ConfiguredClient):
    def __init__(self, addresses, type=peers.LOGIC_P300_CALIBRATION):
        super(LogicFinish, self).__init__(addresses=addresses,
                                          type=type)
        self.ugm = ugm_config_manager.UgmConfigManager('config_8_no_stimulus_fields_tablet').config_to_message()
        self.text_id = 54321
        self.text = u'Dziękujemy za udział w eksperymencie!'
        time.sleep(3)
        self.ready()

    def run(self):
        ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.text)

if __name__ == "__main__":
    LogicFinish(settings.MULTIPLEXER_ADDRESSES).run()
    
