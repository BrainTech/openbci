#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os
import imp
from obci.control.launcher.launcher_tools import expand_path

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
        tpath = expand_path(p_config_file)
        if os.path.exists(tpath):
            base = os.path.basename(tpath).rsplit('.')[0]
            dirname = os.path.dirname(tpath)
            fo, path, des = imp.find_module(base, [dirname])
            mod = imp.load_module(base, fo, path, des)
            l_logic_config = mod.Config()
        else:
            dot = p_config_file.rfind('.')
            if dot < 0:
                mod = ''
                cls = p_config_file
            else:
                mod = p_config_file[:dot]
                cls = p_config_file[dot+1:]
            print("DUPA: "+str(p_config_file))
            tmp = __import__(mod, globals(), locals(), [cls], -1)
            reload(tmp)
            l_logic_config = tmp.__dict__[cls]()
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
        self._current_state_id = self._states[self._current_state_id]['state'][p_decision]
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
