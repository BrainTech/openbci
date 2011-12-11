#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import logic_speller_engine
import speller_graphics_manager as sgm
from ugm import ugm_config_manager
from ugm import ugm_engine
import os, time
import sys

import logic_logging as logger
import logic_multiple_speller_interfaces
LOGGER = logger.get_logger("logic_multiple_speller_engine", "info")

class LogicMultipleSpellerEngine(logic_speller_engine.LogicSpellerEngine):
    def __init__(self, p_server):
        super(LogicMultipleSpellerEngine, self).__init__(p_server)
        self._interfaces = {
            'switch_space': logic_multiple_speller_interfaces.SwitchInterface(p_server)
            }
    def get_requested_configs(self):
        configs = super(LogicMultipleSpellerEngine, self).get_requested_configs()
        configs += sum([i.get_requested_configs() for i in self._interfaces.values()], [])
        configs += ['MS_INSTRUCTION_UGM_CONFIG', 'MS_INSTRUCTION_DURATION','MS_INSTRUCTION_TEXT_ID']
        return configs

    def set_configs(self, configs):
        super(LogicMultipleSpellerEngine, self).set_configs(configs)
        for k, i in self._interfaces.iteritems():
            i.set_configs(configs)
        self._instruction_mgr = ugm_config_manager.UgmConfigManager(self.configs['MS_INSTRUCTION_UGM_CONFIG'])

    def _stop_interfaces(self):
            # *** stop all modules sending decision to logics 
            # and (sometimes) feedback to ugm
            # + stop all inteface-specific modes (eg. blinking, diodes etc.)
        self._server.send_message({
                'type':'switch_control_message',
                'key':'stop',
                'value':''
                })
        self._server.send_message({
                'type':'etr_control_message',
                'key':'stop',
                'value':''
                })
            #diode controlo stop
        self._server.send_message({
                'type':'ugm_control_message',
                'key':'stop_blinking',
                'value':''
                })


    def _prepare_system(self, speller_type):
        self._interfaces[speller_type].prepare_system()

    def _show_instruction(self, speller_type):
        mgr = self._instruction_mgr
        cfg = mgr.get_config_for(int(self.configs['MS_INSTRUCTION_TEXT_ID']))
        cfg['message'] = self._interfaces[speller_type].get_instruction()
        mgr.set_config(cfg)
        eng = ugm_engine.UgmEngine(mgr)
        eng.run(int(self.configs['MS_INSTRUCTION_DURATION']))
        LOGGER.info("Instruction window closed")

    def _fire_speller(self, speller_type):
        self._interfaces[speller_type].fire_speller()

    def fire_speller(self, speller_type):
        LOGGER.info("Fire speller: "+speller_type)
        self._stop_interfaces()
        self._prepare_system(speller_type)
        self._show_instruction(speller_type)
        self._fire_speller(speller_type)
        # teraz niby idzie ode mnie ugm update z pierwszą planszą spellera
