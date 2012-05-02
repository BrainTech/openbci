#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scenarios.video.configs import config_home_8
class Config(config_home_8.Config):
    def _finish_params(self):
        return "'restart_scenario', "+"'~/obci/scenarios/video/bci_ssvep_menu_dummy.ini'"
