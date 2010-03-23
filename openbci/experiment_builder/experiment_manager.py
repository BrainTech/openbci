# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#      Łukasz Polak <l.polak@gmail.com>
#      Joanna Tustanowska <asia.tustanowska@gmail.com>
#
"""Holds Experiment_manager class:
This class is responsible for managing UGM experiments. It loads and holds configs
of those experiments and makes it possible to run them"""

from ugm.ugm_config_manager import UgmConfigManager
from experiment_builder.config.config import CONFIG, USE_MULTIPLEXER, \
USE_DEFAULT_FREQS, DEFAULT_FREQS
#from data_storage import signal_saver_control
import random
import time
import sys

# We must check if we are running this script directly, and if we do,
# then perhaps command-line option overriden config
print (len(sys.argv), sys.argv)
if len(sys.argv) >= 2 and sys.argv[0].find('experiment_manager.py') >= 0 :
    if sys.argv[1] == 'mx-on':
        USE_MULTIPLEXER = True
    elif sys.argv[1] == 'mx-off':
        USE_MULTIPLEXER = False

if USE_MULTIPLEXER:
    from multiplexer.multiplexer_constants import peers, types
    from multiplexer.clients import connect_client
    import variables_pb2
    from data_storage import signal_saver_control

import experiment_logging
LOGGER = experiment_logging.get_logger('experiment_manager')

class Experiment_manager(object):
    """This class is responsible for managing UGM experiments. It loads and holds configs
    of those experiments and makes it possible to run them"""
    def __init__(self, p_config_file=None):
        super(Experiment_manager, self).__init__()
        p_config_file = CONFIG
        self.screens = p_config_file['screens']
        self.sc_configs = []
        self.repeats = p_config_file['repeats']
        
        # set up screens configuration - pair screens with diode freqs
        if not USE_DEFAULT_FREQS:
            self.freq_sets = p_config_file['freqs']
            assert(len(self.screens) == len(self.freq_sets))
            self.sc_configs = [zip(scr, fre) for scr, fre in zip(self.screens,
                self.freq_sets)]
        else:
            assert(DEFAULT_FREQS != None)
            self.sc_configs = [zip(scr, DEFAULT_FREQS) for scr in self.screens]

        LOGGER.info("screens and freqs: \n" + \
                str(self.sc_configs))

        self._shuffle_screens(self.sc_configs)

        LOGGER.debug("SHUFFLED screens and freqs: \n" + \
                str(self.sc_configs))

        self.delay = p_config_file['delay']
        self.config_manager = UgmConfigManager()
        self._connection = None
        

    def _shuffle_screens(self, p_sc_set):
        """ Shuffle screens in each pack """
        for i_nr in range(len(p_sc_set)):
            l_original_screens = p_sc_set[i_nr]
            if len(l_original_screens) > 2:
                l_current_screens = []
                l_last_screen = None
                for i_iterations in range(self.repeats):
                    random.shuffle(l_original_screens)
                    if l_original_screens[0] == l_last_screen:
                        l_tmp = l_original_screens[0]
                        l_original_screens[0] = l_original_screens[1]
                        l_original_screens[1] = l_tmp
                    l_last_screen = l_original_screens[-1]
                    l_current_screens += l_original_screens
            else:
                l_current_screens = p_sc_set[i_nr] * self.repeats
                random.shuffle(l_current_screens)
            p_sc_set[i_nr] = l_current_screens


    def run(self):
        # shuffle screen packs
        random.shuffle(self.sc_configs)
        
        # sleep to synchronize with other modules loading
        time.sleep(10)

        # remember last used frequencies and do not bother diode control too much
        previous_freqs = []

        #FIX FIX FIX FIX FIX l_saver_control = signal_saver_control.SignalSaverControl()
        #FIX FIX FIX FIX FIX l_saver_control.start_saving()
#        i = 0
        for i_screens_pack in self.sc_configs:
            # a pack is a list of tuples (screen + [diode freqs])
            LOGGER.debug("PACK: \n" + str(i_screens_pack))
            for i_screen_conf in i_screens_pack:
#                i = i + 1
#                if i > 3:
#                    break

                LOGGER.info('screen ' + str(i_screen_conf[0]) + '  freqs: ' +\
                        str(i_screen_conf[1]))
                # let ugm read config for new screen...
                self.config_manager.update_from_file(i_screen_conf[0], True)
                # ...then update itself
                self.send_to_ugm()
                # change diode frequencies if needed
                if i_screen_conf[1] != previous_freqs: 
                    self.update_diode_freqs(i_screen_conf[1])
                    previous_freqs = i_screen_conf[1]

                time.sleep(self.delay)
                self._post_screen()
            self._post_screen_package()
        #FIX FIX FIX FIX FIX l_saver_control.finish_saving()

    def send_to_ugm(self):
        if USE_MULTIPLEXER:
            l_type = 0
            l_msg = variables_pb2.UgmUpdate()
            l_msg.type = int(l_type)
            l_msg.value = self.config_manager.config_to_message()
          	      
            # Everything done :) All that is left is to establish connection if needed...
            if not self._connection:
                self._connection = connect_client(type = peers.LOGIC)
            # ...and send message to UGM
            self._connection.send_message(
                message = l_msg.SerializeToString(), 
                type=types.UGM_UPDATE_MESSAGE, flush=True)
        else:
            self.config_manager.update_to_file('ugm_config', True)

    def update_diode_freqs(self, p_freqs):
        l_freq_str = p_freqs
        if not isinstance(p_freqs, basestring):
            l_freq_str = " ".join(['%s' % i for i in p_freqs])

        if USE_MULTIPLEXER:
            l_msg = variables_pb2.Variable()
            l_msg.key = "Freqs"
            l_msg.value = l_freq_str

            # Everything done :) All that is left is to establish connection if needed...
            if not self._connection:
                self._connection = connect_client(type = peers.LOGIC)
            # ...and send message to UGM
            self._connection.send_message(
                message = l_msg.SerializeToString(), 
                type=types.DIODE_UPDATE_MESSAGE, flush=True)

        
    def _post_screen_package(self):
   #     self._play_sound('chime.wav')
        time.sleep(30)
        
    def _post_screen(self):
        pass
   #     self._play_sound('whoosh.wav')
        
    def _play_sound(self, p_wave_file):
        import os
        from wave import open as waveOpen
        from ossaudiodev import open as ossOpen
        l_dir = os.path.dirname(__import__('experiment_builder.resources', 
                                           fromlist=['experiment_builder.resources']).__file__
                               ) + os.path.sep
        s = waveOpen(l_dir + p_wave_file,'rb')
        (nc,sw,fr,nf,comptype, compname) = s.getparams( )
        dsp = ossOpen('/dev/dsp','w')
        try:
            from ossaudiodev import AFMT_S16_NE
        except ImportError:
            if byteorder == "little":
                AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
            else:
                AFMT_S16_NE = ossaudiodev.AFMT_S16_BE
        dsp.setparameters(AFMT_S16_NE, nc, fr)
        data = s.readframes(nf)
        s.close()
        dsp.write(data)
        dsp.close()

    def read_experiment_config(self, p_config_file):
        pass
    
def main():
    l_experiment_manager = Experiment_manager()
    l_experiment_manager.run()

if __name__ == '__main__':
    main()
