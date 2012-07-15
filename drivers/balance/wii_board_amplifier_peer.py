#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from obci_configs import settings, variables_pb2
from drivers import drivers_logging as logger

import cwiid

LOGGER = logger.get_logger("wii_board_amplifier", "debug")

class WiiBoardAmplifier(ConfiguredClient):
    def __init__(self, addresses):
        super(WiiBoardAmplifier, self).__init__(addresses=addresses, type=peers.WII_BOARD_AMPLIFIER)
        LOGGER.info("Start initializing wii board amplifier...")
        LOGGER.info("Please press the red 'connect' button on the balance board, inside the battery compartment.")
        LOGGER.info("Do not step on the balance board.")

	self.wiimote = cwiid.Wiimote()
        self.wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
        self.wiimote.request_status()
        if self.wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
            LOGGER.error('This program only supports the Wii Balance Board')
            self.wiimote.close()
            sys.exit(1)

        balance_calibration = self.wiimote.get_balance_cal()
        self.named_calibration = {'right_top': balance_calibration[0],
                                  'right_bottom': balance_calibration[1],
                                  'left_top': balance_calibration[2],
                                  'left_bottom': balance_calibration[3]
                                  }
        self.ready()


    def _gsc(self, readings, pos):
	reading = readings[pos]
	calibration = self.named_calibration[pos]
	if reading < calibration[1]:
            return 1700 * (reading - calibration[0]) / (calibration[1] - calibration[0])
	else:
            return 1700 * (reading - calibration[1]) / (calibration[2] - calibration[1]) + 1700

    def _get_msg(self):
	self.wiimote.request_status()
	readings = self.wiimote.state['balance']                                   
	try:
            x_balance = (float(self._gsc(readings,'right_top')+self._gsc(readings,'right_bottom'))) / (float(self._gsc(readings,'left_top')+self._gsc(readings,'left_bottom')))
            if x_balance > 1:
                x_balance = (((float(self._gsc(readings,'left_top')+self._gsc(readings,'left_bottom'))) / (float(self._gsc(readings,'right_top')+self._gsc(readings,'right_bottom'))))*-1.)+1.
            else:
                x_balance = x_balance -1.

            y_balance = (float(self._gsc(readings,'left_bottom')+self._gsc(readings,'right_bottom'))) / (float(self._gsc(readings,'left_top')+self._gsc(readings,'right_top')))
            if y_balance > 1:
                y_balance = (((float(self._gsc(readings,'left_top')+self._gsc(readings,'right_top'))) / (float(self._gsc(readings,'left_bottom')+self._gsc(readings,'right_bottom'))))*-1.)+1.
            else:
                y_balance = y_balance -1.
	except:
            x_balance = 1.
            y_balance = 1.


        l_msg = variables_pb2.Sample2D()
        l_msg.x = x_balance
        l_msg.y = y_balance
        l_msg.timestamp = time.time()

        return l_msg
    
    def run(self):
        while True:
            l_msg = self._get_msg()
            self.conn.send_message(message = l_msg.SerializeToString(), 
                                   type = types.WII_BOARD_SIGNAL_MESSAGE, flush=True)
            LOGGER.debug("Send wii board msg:"+str(l_msg.x)+" / "+str(l_msg.y))
            time.sleep(0.05)


if __name__ == "__main__":
    WiiBoardAmplifier(settings.MULTIPLEXER_ADDRESSES).run()
