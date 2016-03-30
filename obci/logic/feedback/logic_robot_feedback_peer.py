#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path, sys, time

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper


import obci.devices.pyrovio.rovio as rovio
from obci.control.common.obci_control_settings import DEFAULT_SANDBOX_DIR
from obci.utils.openbci_logging import log_crash

class LogicRobotFeedback(ConfiguredClient):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(LogicRobotFeedback, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CALIBRATION)
        self.ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()

        self.robot_image_id = int(self.config.get_param("robot_image_id"))

        self._robot = rovio.Rovio('', self.config.get_param('robot_ip'))

        self.tmp1_path = os.path.join(DEFAULT_SANDBOX_DIR, self.config.get_param('tmp_file1'))
        self.tmp2_path = os.path.join(DEFAULT_SANDBOX_DIR, self.config.get_param('tmp_file2'))
        self.paths = [self.tmp1_path, self.tmp2_path]
        self.ready()


    def run(self):
        index = 0
        imgpath = self.paths[index]

        while True:
            try:
                image = self._robot.get_image()
            except:
                self.logger.error("Could not connect to ROBOT. Feedback is OFF!")
            else:
                try:
                    with open(imgpath, 'w') as fil:
                        fil.write(image)
                        fil.close()
                        ugm_helper.send_config_for(self.conn, self.robot_image_id, 'image_path', imgpath)
                        self.logger.debug("Robot image sent " + imgpath + ' id: ' + str(self.robot_image_id))
                        index = int(not index)
                        imgpath = self.paths[index]
                except:
                    self.logger.error("An error occured while writing image to file!")
                time.sleep(0.05)

if __name__ == "__main__":
    LogicRobotFeedback(settings.MULTIPLEXER_ADDRESSES).run()
