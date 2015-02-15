
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, sys
import numpy as np

from obci.configs import settings

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from obci.exps.ventures.data import data_manager

from obci.analysis.balance import wii_utils

class WiiBoardSwayAnalysis(ConfiguredMultiplexerServer):
    """A class used in both calibration and game scenarios in ventures experiment.
    In calibration it uses baseline (from baseline scenario), 
    sends to logic sway levels as percentage of max possible sway (monitor edges or so)
    and stores max user's sways at the end of the scenario.
    In game it uses baseline (from baseline scenario) and max user's sways (From calibration scenario)
    and sends to logic sway levels as a percentage of those maxes."""
    @log_crash
    def __init__(self, addresses, p_type = peers.WII_BOARD_ANALYSIS):
        super(WiiBoardSwayAnalysis, self).__init__(addresses=addresses, type=p_type)
        self._init_params()
        self.logger.info("Starting sway analysis for user: "+str(self._user_id))
        self._set_current_baseline(self._user_id)

        if self._session_name == 'ventures_calibration':
            self._set_raw_maxes()
        elif self._session_name in ['ventures_game', 'ventures_game_training', 'ventures_calibration2']:
            self._set_user_maxes(self._user_id)
        else:
            raise Exception ("Unknown session name - abort")

        self.ready()

    def _init_params(self):
        self._user_id = self.get_param('user_id')
        self._file_name = self.get_param('file_name')
        # 1 if we want to generate dummy current sways, 0 otherwise
        self._dummy = not int(self.get_param('amplifier_online')) 
        self._session_name = self.get_param('session_name')
        # maximum 'possible' sways. in calibration it should be a kind of monitor edges
        # in game it should be user's maximum sways calculated a moment ago in calibration scenario.
        self._maxes = {'up':-1.0,
                       'right':-1.0,
                       'down':-1.0,
                       'left':-1.0,
                   }
        # Current user's maximum sways. in game scenario it is rather not needed
        # but in calibration scenario it will be stored at the end of the scenario
        # and used in next game scenario as 'maximu possible sways'
        self._current_maxes = {'up':-1.0,
                               'right':-1.0,
                               'down':-1.0,
                               'left':-1.0,
                           }
    @log_crash
    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_SIGNAL_MESSAGE:
            if self._dummy:
                sway_direction, sway_level = self._calculate_dummy_sway()
            else:
                #calculate and send current sway direction and level
                v = variables_pb2.SampleVector()
                v.ParseFromString(mxmsg.message)
                X, Y = [], []
                for s in v.samples:#todo - refactor in regard to utils/wii_2d_router
                    sum_mass = sum(s.channels[0:4])
                    if sum_mass<200:
                        break
                    x, y = wii_utils.get_x_y(s.channels[0], s.channels[1], s.channels[2], s.channels[3])
                    X.append(x)
                    Y.append(y)
                if len(X):
                    sway_direction, sway_level = self._calculate_real_sway(np.mean(X), np.mean(Y))
                else:
                    sway_direction, sway_level = 'baseline', 0

            msg = variables_pb2.IntVariable()
            msg.key = sway_direction
            msg.value = sway_level
            self.conn.send_message(message=msg.SerializeToString(),
                                   type=types.WII_BOARD_ANALYSIS_RESULTS, flush=True)
        elif mxmsg.type == types.ACQUISITION_CONTROL_MESSAGE:
            # storing user's current maxes makes sens only in calibration scenario ...
            if self._session_name != 'ventures_calibration':
                self.logger.info("Got acquisition_control_message, but session name is "+self._session_name+" . Just exit quietly ...")
                sys.exit(0)
            else: #self._session_name == 'ventures_calibration'
                self.logger.info("Got acquisition_control_message in calibration session. Start storing calibration results (maxes)... ")
                self._store_calibration_results()
                sys.exit(0)
        else:
            self.logger.warning("Unrecognised message type!!!")
        self.no_response()

    def _calculate_dummy_sway(self):
        try:
            self._dummy_v
        except:
            self._dummy_v = 0
            self._dummy_d = 0
            self._dummy_dirs = ['up', 'right', 'down', 'left', 'baseline']

        self._dummy_v = self._dummy_v + 0.25
        if not (self._dummy_v % 100):
            self._dummy_d = (self._dummy_d + 1) % 5
        return self._dummy_dirs[self._dummy_d], (int(self._dummy_v) % 70)

    def _calculate_real_sway(self, x, y):
        """Return two values: direction, level where
        - direction - is a string in ['up', 'right', 'down', 'left', 'baseline'] representing direction of sway
        - level - is a int in [0 ... 100 or even more] representing a percentage of max possible sway
        """
        if (y>self.yc and x<=self.xc and y>=-x+(self.yc+self.xc)) or (y>self.yc and x>self.xc and y>=x+(self.yc-self.xc)):
            value = np.abs(y-self.yc)-np.abs(self.yb)
            direction = 'up'

        elif (y<=self.yc and x<=self.xc and y<=x+(self.yc-self.xc)) or (y<=self.yc and x>self.xc and y<=-x+(self.yc+self.xc)):
            value = np.abs(y-self.yc)-np.abs(self.yb)
            direction = 'down'

        elif (x<=self.xc and y>self.yc and y<-x+(self.yc+self.xc)) or (y<=self.yc and x<=self.xc and y>x+(self.yc-self.xc)):
            value = np.abs(x-self.xc)-np.abs(self.xa)
            direction = 'left'

        elif (y>self.yc and x>self.xc and y<x+(self.yc-self.xc)) or (y<=self.yc and x>self.xc and y>-x+(self.yc+self.xc)):
            value = np.abs(x-self.xc)-np.abs(self.xa)
            direction = 'right'

        if value<=0:
            direction = 'baseline'
            return direction, 0

        if self._session_name == 'ventures_calibration':
            self._update_current_maxes(direction, np.abs(value))

        return direction, int((value/self._maxes[direction])*100)

            
    def _set_current_baseline(self, user_id):
        """Get last user's baseline from database
        and store it on slot for further use."""
        xa, ya, xb, yb, xc, yc, t = data_manager.baseline_get_last(user_id)
        self.logger.info("Take baseline from time: "+t+" while current time is: "+data_manager.current_time_to_string())
        if (time.time() - data_manager.time_from_string(t)) > 10*60:
            self.logger.warning("WARNING!!! Baseline for this scenario was collected more than 10 minutes ago!!! Is it expected???")

        if self._dummy:
            self.xa = 0.005
            self.ya = 0.005
            self.xb = 0.005
            self.yb = 0.005
            self.xc = 0.0
            self.yc = 0.0
        else:
            self.xa = float(xa)
            self.ya = float(ya)
            self.xb = float(xb)
            self.yb = float(yb)
            self.xc = float(xc)
            self.yc = float(yc)

    def _set_user_maxes(self, user_id):
        """Get last user's calibration data - his maxes - from database
        and store it for further use. Used in game scenario.
        """
        up, right, down, left, t = data_manager.calibration_get_last(user_id)
        self.logger.info("Take maxes from calibration on time: "+t+" while current time is: "+data_manager.current_time_to_string())
        if (time.time() - data_manager.time_from_string(t)) > 10*60:
            self.logger.warning("WARNING!!! Calibration for this game scenario was collected more than 10 minutes ago!!! Is it expected???")
        self._maxes = {'up':float(up), 
                       'right':float(right), 
                       'down':float(down), 
                       'left':float(left)
                       }
        self.logger.info("_maxes set to user maxes which is: "+str(self._maxes))

    def _set_raw_maxes(self):
        """Set maxes to max possible values, representing edges of the monitor.
        Used in calibration scenario.
        """
        self._maxes = {'up':float(self.get_param('raw_max_up')),
                       'right':float(self.get_param('raw_max_right')),
                       'down':float(self.get_param('raw_max_down')),
                       'left':float(self.get_param('raw_max_left'))
                      }
        self.logger.info("_maxes set to raw maxes which is: "+str(self._maxes))

    def _update_current_maxes(self, sway_direction, sway_level):
        if self._current_maxes[sway_direction] < sway_level:
            self._current_maxes[sway_direction] = sway_level
            self.logger.info("_current_maxes updated. Now it looks like: "+str(self._current_maxes))

    def _store_calibration_results(self):
        self.logger.info('Start storing calibration results. Calibration maxes calculated: '+str(self._current_maxes))
        data_manager.calibration_set(self._user_id, 
                                     self._current_maxes['up'],
                                     self._current_maxes['right'],
                                     self._current_maxes['down'],
                                     self._current_maxes['left'],
                                     self._file_name)
        self.logger.info('Calibration data properly stored for user: '+self._user_id+' with: '+str(self._current_maxes))

if __name__ == "__main__":
    WiiBoardSwayAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
