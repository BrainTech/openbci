#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scenarios.video.configs import config_robot_8
class Config(config_robot_8.Config):
    def _finish_params(self):
        return "'restart_scenario', "+"'~/obci/scenarios/video/bci_ssvep_menu.ini'"
