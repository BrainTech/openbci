#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient
from drivers.switch import external_audio_switch as audio_switch

from configs import settings, variables_pb2
import random, time, sys

from drivers import drivers_logging as logger
LOGGER = logger.get_logger("external_switch_amplifier_peer", "info")

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
                LOGGER.info("Send switch message")
                self.conn.send_message(message = "",
                                       type = types.SWITCH_MESSAGE, flush=True)            
            else:
                LOGGER.debug("No decision. Keep on...")
if __name__ == "__main__":
    ExternalSwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

