#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, sys, time

from obci.control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types

from obci.configs import settings,variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper

class LogicGiveID(ConfiguredClient):
    def __init__(self, addresses):
        super(LogicGiveID, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CALIBRATION)
        
        self.ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.file_id_path = self.config.get_param("file_id_path")
        self.file_id_name = self.config.get_param("file_id_name")
        self.text_id = int(self.config.get_param("ugm_text_id"))
        self.s_id = self.config.get_param("scenarios_id")
        self._init_id()
        self._init_id_file()
        time.sleep(3)
        self.ready()
        
    def _init_id(self):
        self.ID = self.s_id + '_'+ ("").join(str(part) for part in time.localtime()[1:5])
    def _init_id_file(self):
        file_dir = os.path.expanduser(os.path.normpath(self.file_id_path))
        id_file = open(os.path.normpath(os.path.join(file_dir, 
                                                     self.file_id_name)), 'w')
        id_file.write(str(self.ID))
        id_file.close()
    def run(self):
        ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.ID)

if __name__ == "__main__":
    LogicGiveID(settings.MULTIPLEXER_ADDRESSES).run()            
        
