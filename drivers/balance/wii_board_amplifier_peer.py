#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, time

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

import pygame

class WiiBoardAmplifier(ConfiguredClient):
    @log_crash
    def __init__(self, addresses):
        super(WiiBoardAmplifier, self).__init__(addresses=addresses,
                                                type=peers.AMPLIFIER)
        self.operating_system = self.config.get_param('operating_system')
        if self.operating_system == 'Linux':
            import wiiboard

            self.logger.info("Start initialization wii board amplifier")
            self.board = wiiboard.Wiiboard()
            self.logger.info("Connecting to Wiiboard..")
            self.logger.info("Please press the red 'connect' button on the balance board, inside the battery compartment.")
            try:
                bord_address = self.board.discover()
                self.logger.info("Found Wiiboard at address " + bord_address)
            except Exception as e:
                self.logger.error(e)
                sys.exit(1)
            try:
                self.board.connect(bord_address)
                self.logger.info("Connected to Wiiboard at address " + bord_address)

            except Exception as e:
                self.logger.error(e)
                sys.exit(1)

        elif self.operating_system == 'Windows':
            import wiiboard_win as wiiboard

            self.logger.info("Start initialization wii board amplifier")
            self.board = wiiboard.Wiiboard()
            try:
                self.logger.info("Connecting to Wiiboard...")
                self.board.connect()
            except Exception as e:
                self.logger.error(e)
                sys.exit(1)
        else:
            self.logger.info("wrong operating system : operating_system=" + operating_system + " (can be Linux or Windows)")
            sys.exit(1)
        global wiiboard
        pygame.init()
        self.done = False
        self.ready()

    def get_msg(self, event):
        packet = variables_pb2.SampleVector()
        sample = packet.samples.add()
        sample.timestamp = time.time()
        #print event.mass.topRight, event.mass.bottomRight, event.mass.topLeft, event.mass.bottomLeft, event.mass.totalWeight
        if event.mass.totalWeight < 1:
            x = 0 # ?
            y = 2 # ?
        else:
            x = ((event.mass.topRight + event.mass.bottomRight) -
                 (event.mass.topLeft + event.mass.bottomLeft))/event.mass.totalWeight
            y = ((event.mass.topRight + event.mass.topLeft) -
                 (event.mass.bottomRight + event.mass.bottomLeft))/event.mass.totalWeight
        sample.channels.extend([x, y])     
        return packet

    def disconnect(self):
        self.board.disconnect()

    @log_crash
    def run(self):
        if self.operating_system == 'Windows': 
			self.board.startThread()
        while (not self.done):
            for event in pygame.event.get():
                if event.type == wiiboard.WIIBOARD_MASS:
                    msg = self.get_msg(event)
                    self.conn.send_message(message = msg.SerializeToString(),
                                           type = types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
                elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
                    self.logger.info("Button pressed!")
                    #self.disconnect()
                elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE:
                    self.logger.info("Button released")
                elif event.type == wiiboard.WIIBOARD_DISCONNECTED:
                    self.logger.info("Wiiboard diconected")
                    self.done = True
        pygame.quit()

if __name__ == "__main__":
    WiiBoardAmplifier(settings.MULTIPLEXER_ADDRESSES).run()
