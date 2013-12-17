
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from obci.control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types
from obci.utils import context as ctx
from obci.configs import settings,variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper

class LogicAlpha(ConfiguredClient):
    def __init__(self, addresses, type=peers.LOGIC_P300_CALIBRATION):
        super(LogicAlpha, self).__init__(addresses=addresses,
                                          type=type)
        self.ready()

    def run(self):
        pass

if __name__ == "__main__":
    LogicAlpha(settings.MULTIPLEXER_ADDRESSES).run()
    
