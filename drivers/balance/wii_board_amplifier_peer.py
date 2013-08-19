#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, time

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

import pygame
import wiiboard

class WiiBoardAmplifier(ConfiguredClient):
    @log_crash
     def __init__(self, addresses):
          super(WiiBoardAmplifier, self).__init__(addresses=addresses, 
                                                  type=peers.AMPLIFIER)
          self.logger.info("Start initializwiing wii board amplifier")
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
          pygame.init()
          self.done = False
          self.ready()

     def get_msg(self, event):
          packet = variables_pb2.SampleVector()
          sample = packet.samples.add()
          sample.timestamp = time.time()
          print event.mass.topRight, event.mass.bottomRight, event.mass.topLeft, event.mass.bottomLeft, event.mass.totalWeight
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
          while (not self.done):
               for event in pygame.event.get():
                    if event.type == wiiboard.WIIBOARD_MASS:
                         msg = self.get_msg(event)
                         self.conn.send_message(message = msg.SerializeToString(), 
                                                type = types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
                         self.logger.info("Send wii board msg:"+str(msg.x)+" / "+str(msg.y))
                    elif event.type == wiiboard.WIIBOARD_BUTTON_PRESS:
                         self.logger.info("Button pressed!")
                         self.disconnect()
                    elif event.type == wiiboard.WIIBOARD_BUTTON_RELEASE: #niepotrzebne?
                         self.logger.info("Button released")
                    elif event.type == wiiboard.WIIBOARD_DISCONNECTED:
                         self.logger.info("Wiiboard diconected")
                         self.done = True
          pygame.quit()
                 
if __name__ == "__main__":
    WiiBoardAmplifier(settings.MULTIPLEXER_ADDRESSES).run()
