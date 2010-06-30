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
from experiment_builder.config.config import USE_MULTIPLEXER 

import random
import time
import sys
import os.path
from openbci.tags import tagger

TAGGER = tagger.get_tagger()

# We must check if we are running this script directly, and if we do,
# then perhaps command-line option overriden config
print (len(sys.argv), sys.argv)
config_file_name = None
config_module_name = None
if len(sys.argv) >= 3 and sys.argv[0].find('experiment_manager.py') >= 0 :
    if sys.argv[1] == 'mx-on':
        USE_MULTIPLEXER = True
    elif sys.argv[1] == 'mx-off':
        USE_MULTIPLEXER = False
    if len(sys.argv) >= 3:
        config_file_name = sys.argv[2]
    if len(sys.argv) >= 4:
        config_module_name = sys.argv[3]

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
    def __init__(self, p_config_name=None, p_config_module='experiment_manager.config'):
        super(Experiment_manager, self).__init__()

        self.config_file = self.read_experiment_config(p_config_name, p_config_module)
        print self.config_file
        self.screens = self.config_file['screens']
        self.sc_configs = []
        self.repeats = self.config_file['repeats']
        self.readable_names = self.config_file['readable_names']
        self.sq_numbers = self.config_file['square_numbers']
        
        # set up screens configuration - pair screens with diode freqs
        if not self.config_file.get('USE_DEFAULT_FREQS'):
            self.freq_sets = self.config_file['freqs']
            assert(len(self.screens) == len(self.freq_sets))
            self.sc_configs = [zip(scr, fre, s_no) for scr, fre, s_no in zip(self.screens,
                self.freq_sets, self.sq_numbers)]
        else:
            def_freqs = self.config_file['DEFAULT_FREQS']
            assert(def_freqs != None)
            self.sc_configs = [zip(scr, def_freqs) for scr in self.screens]

        LOGGER.info("screens and freqs: \n" + \
                str(self.sc_configs))

        self._shuffle_screens(self.sc_configs)

        LOGGER.debug("SHUFFLED screens and freqs: \n" + \
                str(self.sc_configs))

        self.delay = self.config_file['delay']
        self.config_manager = UgmConfigManager()
        self._connection = None
        self._screen_sounds = self.config_file.get('sounds', None)
        self._screen_look_num = 0
        if self._screen_sounds:
            import pygame
            pygame.init()
            for i in range(len(self._screen_sounds)):
                self._screen_sounds[i] = os.path.join(self.config_file['dir'], self._screen_sounds[i])
        

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
        time.sleep(5)
        
        if USE_MULTIPLEXER:
            l_saver_control = signal_saver_control.SignalSaverControl()
            l_saver_control.start_saving()
            time.sleep(1)
        
        l_time = time.time()
        TAGGER.send_tag(l_time, l_time, "experiment_start",
                {
                    "exp_config" : self.config_file
                    })

        for i_screens_pack in self.sc_configs:
            # a pack is a list of tuples (screen + [diode freqs])
            self._pre_screen_package(i_screens_pack)
            LOGGER.debug("PACK: \n" + str(i_screens_pack))
            for i_screen_conf in i_screens_pack:

                self._pre_screen(i_screen_conf)
                LOGGER.info('screen ' + str(i_screen_conf[0]) + '  freqs: ' +\
                        str(i_screen_conf[1]))
                # let ugm read config for new screen...
                self.config_manager.update_from_file(i_screen_conf[0], True)
                # ...then update itself
                self.send_to_ugm()
                # change diode frequencies 
                self.update_diode_freqs(i_screen_conf[1])

                time.sleep(self.delay)
                self._post_screen(i_screen_conf)
                if self.config_file['make_breaks']:
                    l_time = time.time()
                    TAGGER.send_tag(l_time, l_time, "experiment_update", 
                        {
                            "break" : True,
                            "Freqs" : self.config_file['break_freqs'],
                            "delay" : self.config_file['break_len'] # TODO
                        }) 
                    self.update_diode_freqs(self.config_file['break_freqs'])
                    time.sleep(self.config_file['break_len'])

            self._post_screen_package(i_screens_pack)
        l_time = time.time()
        TAGGER.send_tag(l_time, l_time, "experiment_end",
                {})
        if USE_MULTIPLEXER:
            l_saver_control.finish_saving()

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
            # ...and send message to diode control
            self._connection.send_message(
                message = l_msg.SerializeToString(), 
                type=types.DIODE_UPDATE_MESSAGE, flush=True)
    
    def _pre_screen_package(self, p_screen_package):
        print('New screen package: ' + str(p_screen_package))
        self._screen_look_num = 0
        
    def _post_screen_package(self, p_screen_package):
    #  self._play_sound('chime.wav')
        time.sleep(30)
    
    def _pre_screen(self, p_screen_config):
        print('New screen: ' + str(p_screen_config[0]))
        # TODO: wybieranie pola do koncentracji, dzwiek oznajmiajacy o tym, zapis do tagu
        l_screen_config_name = p_screen_config[0]
        l_time = time.time()
        if l_screen_config_name in self.readable_names:
            l_screen_name = self.readable_names[l_screen_config_name]
        else:
            l_screen_name = l_screen_config_name
        self._play_sound()
        TAGGER.send_tag(l_time, l_time, "experiment_update", 
                        {
                            "concentrating_on_field" : p_screen_config[2],#self._screen_look_num,
                            "screen" : l_screen_name,
                            "Freqs" : p_screen_config[1],
                            "delay" : self.config_file['delay'] # TODO
                        }) 
    
    def _post_screen(self, p_screen_config):
    #   self._play_sound('whoosh.wav')
        pass
        
    def _play_sound(self):
        if not self._screen_sounds:
            return 
        import pygame
        p_wave_file = self._screen_sounds[self._screen_look_num]
        pygame.mixer.Sound(p_wave_file).play()
        self._screen_look_num = (self._screen_look_num + 1) % len(self._screen_sounds)


    def read_experiment_config(self, p_config_name, p_module_prefix='experiment_builder.config'):
        module_prefix = p_module_prefix
        config_module = None
        if p_config_name == None:
            config_module = __import__(module_prefix + '.config', \
                    fromlist=['CONFIG'])
        else:
            try:
                config_module = __import__(module_prefix +'.'+ p_config_name, \
                        fromlist=['CONFIG'])
            except: 
                print "INVALID EXPERIMENT CONFIG NAME! ", p_config_name
                raise
        return config_module.CONFIG 


def main():
    l_experiment_manager = Experiment_manager(config_file_name, config_module_name)
    l_experiment_manager.run()

if __name__ == '__main__':
    main()
