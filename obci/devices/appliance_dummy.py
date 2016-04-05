#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import sys
from obci.devices import devices_logging as logger
LOGGER = logger.get_logger('appliance_dummy', 'info')
class Blinker(object):
    def __init__(self):
        LOGGER.info("Init")

    def open(self):
        LOGGER.info("Open")
 
    def close(self):
        LOGGER.info("Close")
 
    def send(self, value):
        LOGGER.info("Send: "+str(value))
 
    def blinkSSVEP(self,d, p1, p2):
        LOGGER.info("blinkSSVEP: "+str(d)+', '+str(p1)+', '+str(p2))
 
    def blinkP300(self,d):
        LOGGER.info("blinkP300: "+str(d))

    def on(self):
        LOGGER.info("On")

    def off(self):
        LOGGER.info("Off")
