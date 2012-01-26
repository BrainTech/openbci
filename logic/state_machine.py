#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

class StateMachine(object):
    """A facade between config file and logic_engine class.
    Provides usefull methods to get and set (by now in-memory) configuration.
    """
    def __init__(self, p_logic_config_name):
        """import p_logic_config_name, store state configs for every state."""
        self._config_file = p_logic_config_name
        self.update_from_file()

    def update_from_file(self, p_config_file=None):
        if not  p_config_file:
            p_config_file = self._config_file
        l_logic_config = __import__(p_config_file)
        reload(l_logic_config)
        self._states = []
        for i_state_ind in range(l_logic_config.number_of_states):
            l_state = dict()
            for i_state_variable in l_logic_config.states_configs:
                l_state[i_state_variable] = l_logic_config.__dict__[i_state_variable][i_state_ind] #TODO - shold i copy?
            self._states.append(l_state)

        self._current_state_id = 0

        # Get also config not assigned to any particular state.
        self._other_configs = dict()

        for i_config_var in l_logic_config.other_configs:
            self._other_configs[i_config_var] = (l_logic_config.__dict__[i_config_var]) #TODO - #TODO - should i copy?
    def set_next_state(self, p_decision):
        """"Go to next state from current state as a resutl of p_decision."""
        self._current_state_id = self._states[self._current_state_id]['screen'][p_decision]
    def get_current_state(self):
        """Return current state id (number)."""
        return self._current_state_id

    def get_state_param(self, p_state_id, p_param_id):
        """Return p_param_id paremeter for p_state_id state."""
        return self._states[p_state_id][p_param_id]

    def get_current_state_param(self, p_param_id):
        """Return p_param_id parameter for current state."""
        return self.get_state_param(self._current_state_id, p_param_id)

    def get_other_param(self, p_param_id):
        """Return p_param_id parameter from other_configs slot."""
        return self._other_configs[p_param_id]

    def set_state_param(self, p_state_id, p_param_id, p_param_value):
        """For state p_state_id set its p_param_id to p_param_value."""
        self._states[p_state_id][p_param_id] = p_param_value

    def get_number_of_states(self):
        return len(self._states)
