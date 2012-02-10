#!/usr/bin/env python
# -*- coding: utf-8 -*-
from scenarios.video.configs import config_settings_8
class Config(config_settings_8.Config):
    def __init__(self):
        self._scenarios = [
            "~/obci/scenarios/video/bci_ssvep_menu_dummy.ini",
            "~/obci/scenarios/video/calibration_ssvep_dummy.ini",
            "~/obci/scenarios/video/bci_p300_menu_dummy.ini",
            "~/obci/scenarios/video/calibration_ssvep_dummy.ini",
            "~/obci/scenarios/video/bci_ssvep_menu_dummy_c1.ini",
            "~/obci/scenarios/video/bci_ssvep_menu_dummy_c2.ini",
            "~/obci/scenarios/video/bci_ssvep_menu_dummy_c3.ini",
            "~/obci/scenarios/video/bci_ssvep_menu_dummy.ini",
            ]
        super(Config, self).__init__()

    def _scenario(self, i):
        return self._scenarios[i]
