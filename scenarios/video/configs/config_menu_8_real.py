#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scenarios.video.configs import config_menu_8
class Config(config_menu_8.Config):
    def _speller_scenario(self):
        return  "~/obci/scenarios/video/bci_ssvep_speller.ini"

    def _robot_scenario(self):
        return  "~/obci/scenarios/video/bci_ssvep_speller.ini"
    #return "~/obci/scenarios/video/bci_ssvep_robot.ini"

    def _home_scenario(self):
        return  "~/obci/scenarios/video/bci_ssvep_speller.ini"
    #return "~/obci/scenarios/video/bci_ssvep_home.ini"

    def _settings_scenario(self):
        return  "~/obci/scenarios/video/bci_ssvep_speller.ini"
       #return "~/obci/scenarios/video/bci_ssvep_settings.ini"
