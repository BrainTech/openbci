#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path, sys, time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci_configs import settings, variables_pb2
from gui.ugm import ugm_config_manager
from gui.ugm import ugm_helper

from utils import streaming_debug
import devices.pyrovio.rovio as rovio
from common.obci_control_settings import DEFAULT_SANDBOX_DIR


from logic import logic_logging as logger
LOGGER = logger.get_logger("logic_robot_feedback2", "info")
DEBUG = False

class LogicRobotFeedback2(ConfiguredMultiplexerServer):
    """Use with some signal source ON, that fires often self._Handle_message.
    Eg. amplifier... Unlike LogicRobotFeedback, this feedback handles control messages.
    Used in multiple apps..."""
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(LogicRobotFeedback2, self).__init__(addresses=addresses,
                                          type=peers.ROBOT_FEEDBACK)

        self.ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.robot_image_id = int(self.config.get_param("robot_image_id"))
        self._robot = rovio.Rovio('', self.config.get_param('robot_ip'))
        self.tmp1_path = os.path.join(DEFAULT_SANDBOX_DIR, self.config.get_param('tmp_file1'))
        self.tmp2_path = os.path.join(DEFAULT_SANDBOX_DIR, self.config.get_param('tmp_file1'))
        self.paths = [self.tmp1_path, self.tmp2_path]
        self.index = 0
        self.imgpath = self.paths[self.index]
        self._last_time = time.time()
        self.is_on = False
        if DEBUG:
            self.debug = streaming_debug.Debug(128,
                                               LOGGER,
                                               4)
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.ROBOT_FEEDBACK_CONTROL:
            if mxmsg.message == 'start':
                LOGGER.info("Got start message. Start robot feedback!!!")
                self.is_on = True
            elif mxmsg.message == 'stop':
                LOGGER.info("Got stop message. Stop robot feedback!!!")
                self.is_on = False
                ugm_helper.send_logo(self.conn, 'gui.ugm.resources.bci.png')#todo - CEBIT fix... should be done somewhere in logic, but to ensure that robot feed will not overwrite log do it here...
            else:
                LOGGER.warning("Unrecognised control message:" + str(mxmsg.message))

        if DEBUG:
            self.debug.next_sample()
        diff = (time.time() - self._last_time)
        if not self.is_on:
            self.no_response()
            return
        elif diff > 1.0:
            self._last_time = time.time()
            LOGGER.error("Last time bigger than 1.0... give it a chance next time. ...")
            self.no_response()
            return
        elif  diff > 0.2:
            LOGGER.debug("Last time bigger than 0.2... don`t try read image for a while ...")
            self.no_response()
            return
        elif diff > 0.05:
            self._last_time = time.time()
            t = time.time()
            try:
                LOGGER.debug("Start getting image...")
                image = self._robot.get_image(timeout=0.5)
                LOGGER.debug("Succesful get_image time:"+str(time.time()-t))
            except:
                LOGGER.error("UNSuccesful get_image time:"+str(time.time()-t))
                LOGGER.error("Could not connect to ROBOT. Feedback is OFF!")
            else:
                try:
                    with open(self.imgpath, 'w') as fil:
                        fil.write(image)
                        fil.close()
                        ugm_helper.send_config_for(self.conn, self.robot_image_id, 'image_path', self.imgpath)
                        LOGGER.debug("Robot image sent " + self.imgpath + ' id: ' + str(self.robot_image_id))
                        self.index = int(not self.index)
                        self.imgpath = self.paths[self.index]
                except Exception, e:
                    LOGGER.error("An error occured while writing image to file!")
                    print(repr(e))
            self.no_response()
            return
        else:
            self.no_response()
            return

if __name__ == "__main__":
    LogicRobotFeedback2(settings.MULTIPLEXER_ADDRESSES).loop()