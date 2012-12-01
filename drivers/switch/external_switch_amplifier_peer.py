#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from drivers.switch import external_audio_switch as audio_switch

from obci.configs import settings, variables_pb2
import random, time, sys

class ExternalSwitchAmplifier(ConfiguredClient):
    def __init__(self, addresses):
        super(ExternalSwitchAmplifier, self).__init__(addresses=addresses,
                                          type=peers.EXTERNAL_SWITCH_AMPLIFIER)
        self.driver = audio_switch.AudioSwitch()
        self.ready()

    def run(self):
        while True:
            dec = self.driver.next()
            if dec:
                self.logger.info("Send switch message")
                self.conn.send_message(message = "",
                                       type = types.SWITCH_MESSAGE, flush=True)            
            else:
                self.logger.debug("No decision. Keep on...")
            time.sleep(0.1)
if __name__ == "__main__":
    ExternalSwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

