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
import logic_engine
import speller_graphics_manager as sgm
class LogicSpellerEngine(logic_engine.LogicEngine):
    def __init__(self, p_server):
        self._menu_state = [0, 0, 0]
        self._message = ''
        super(LogicSpellerEngine, self).__init__(p_server)

    # --------------------------------------------------------------------------
    # ------------------ actions available in config ---------------------------
    def backspace(self):
        """Run backspace action -> truncate self._message.
        A place where this action is defined to be fired
        is speller config file.
        """
        self._message = self._message[:len(self._message) - 1]

    def say(self):
        """Run say action -> run external program with self._message
        as a paramtere.
        A place where this action is defined to be fired
        is speller config file.
        """
        #run_ext('milena '+self._message)
        pass

    def msg(self, p_message):
        """Update stored message considering:
        """
        self._message = ''.join([self._message, p_message])


    
    def solve_menu(self, p_menu_id):
        """For given main menu id p_menu_id (this is the menu in state 0)
        return an index of graphics to be displayed in ugm.
        """
        return self._menu_state[p_menu_id]

    # ------------------ actions available in config ---------------------------
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # ---------- methods for config updates and other updates  -----------------
    def _update_global_gui(self):
        """Sent to self._server current logic data:
        - current message,
        """
        l_graphics_string = sgm.SpellerGraphicsManager().pack_one(self._message, 909)
        self._server.send_message({
                'value':l_graphics_string,
                'type':'ugm_update_message'})
        super(LogicSpellerEngine, self)._update_global_gui()
    def _update_main_menu(self, p_decision):
        """Update locally stored menu_state. The method is fired
        when we are in 0 state and p_decision has been made by the user.
        """
        try:
            self._menu_state[p_decision] = (self._menu_state[p_decision] + 1) % 2
        except IndexError:
            # In case p_decision is not about dynamic main menu, eg.
            # we have some other actions available from state 0 that are
            # not dynamic like main menu.
            pass

    # ---------- methods for config updates and other updates  -----------------
    # --------------------------------------------------------------------------

    def _run_additional_actions(self, p_decision_object):
        l_dec = p_decision_object.decision
                        # Update dynamic main menu state if current state is initial state.      
        if self._state_machine.get_current_state() == 0:
            self._update_main_menu(l_dec)


#TODO 
# - napisac testy

#kto ustawia numOfFreq?
#ocb z tym pausepoint?
