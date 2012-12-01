#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.utils import context as ctx
from obci.logic import state_machine
from obci.logic import logic_helper
from obci.configs import settings, variables_pb2

class LogicDecision(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses, type=peers.LOGIC_DECISION):
        super(LogicDecision, self).__init__(addresses=addresses,
                                         type=type)
        self._state_machine = state_machine.StateMachine(self.config.get_param("logic_decision_config"))

    def handle_message(self, mxmsg):
        if (mxmsg.type == types.DECISION_MESSAGE):
            l_decision = int(mxmsg.message)
            self.logger.info("Got decision: "+str(l_decision))
            # Fire an action for current state and current decision
            self._run_pre_actions(l_decision)

            l_action = self._compute_current_actions()[l_decision]
            if len(l_action) > 0: #if l_action is not an empty string
                eval(u"".join([u"self.", l_action]))
            
            # Go to next state...
            self._state_machine.set_next_state(l_decision)

            self._run_post_actions(l_decision)
            
        else:
            self.logger.info("Got unrecognised message type: "+mxmsg.type)

        self.no_response()

    def _run_pre_actions(self, p_decision):
        pass

    def _run_post_actions(self, p_decision):
        pass

    # --------------------------------------------------------------------------
    # ------------------ actions available in config ---------------------------
    def mult_action(self, actions):
        for a in actions:
            eval(u"".join([u"self.", a]))

    def run_ext(self, p_program_string):
        """Run external program p_program_string."""
        try:
            os.system(p_program_string)
        except Exception, e:
            self.logger.error("Couldnt run external "+p_program_string+" with error:")
            self.logger.error(str(e))

    def finish(self):
        self.logger.info("Finish LOGIC")
        #sys.exit(1)

            
    # ------------------ actions available in config ---------------------------
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # ---------- methods for config updates and other updates  -----------------

    def _compute_current_actions(self):
        """Return collection of strings representing current`s state actions. 
        See _compute_current_param for details.
        """
        return self._compute_current_param('actions', 'actions_solver')

    def _compute_current_param(self, p_param, p_param_solver):
        """Return a collection of strings representing ... someting ...
        depending on p_param.
        The point is that we have p_param in config as a collection of objects.
        By now two situations might occur:
        1) all elements in config are strings
        2) some elements in config are collections.
        If we have string it`s cool - we just return strings.
        If we have collection, a string to be returned must be computed.
        We use p_param_solver config parameter to get what we want.
        p_param_solver is a collection of string representing methods
        that allow to decide which element from p_param`s collection
        is now CURRENT.
        """
        l_config_param = self._state_machine.get_current_state_param(p_param)
        l_current_param = [u""]*len(l_config_param)
        #Above a collection to be filled from l_config_param and returned.
        l_curr_state = self._state_machine.get_current_state()
        for i_index, i_elem in enumerate(l_config_param):
            # Below a tricky (= FAST) method to test if an object
            # is a collection or string. More often it`ll be string
            # so we 'try' to test it as it were string.
            try:
                i_elem + '' #test if i_gr_elem is a string
            except TypeError: #i_gr_elem is a sequence
                # Get a collection of strings representing methods
                # that resolve current state`s param
                l_solvers = self._state_machine.get_state_param(l_curr_state, p_param_solver)
                # Set current param to a chosen element from config
                l_str_method = u"".join([u"self.", l_solvers[i_index]])
                l_current_param[i_index] = l_config_param[i_index][eval(l_str_method)]
            else: # We have string in config so just copy it ...
                l_current_param[i_index] = l_config_param[i_index]
        return l_current_param
        
    # ---------- methods for config updates and other updates  -----------------
    # --------------------------------------------------------------------------
