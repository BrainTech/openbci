#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scenarios.video.configs import config_menu_8
class Config(config_menu_8.Config):
    def __init__(self):
        self._speller_scenario = "~/obci/scenarios/video/bci_ssvep_speller_dummy.ini"
        self._robot_scenario = "~/obci/scenarios/video/bci_ssvep_robot_dummy.ini"
        self._home_scenario = "~/obci/scenarios/video/bci_ssvep_hoem_dummy.ini"
        self._settings_scenario = "~/obci/scenarios/video/bci_ssvep_settings_dummy.ini"
        super(Config, self).__init__()
