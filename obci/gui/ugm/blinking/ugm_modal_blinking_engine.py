#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
# Marian Dovgialo <marian.dowgialo@gmail.com>

# requires pyo for sound
from __future__ import print_function
from ugm_blinking_engine import UgmBlinkingEngine
import sys

from obci.devices.haptics.HapticsControl import HapticStimulator
from obci.utils import context as ctx
from obci.gui.ugm import ugm_engine
from PyQt4 import QtCore
import time
import os.path
import random

HALFBLINKID=-1

class pygameSoundCompat:
    def __init__(self, sound):
        self.sound = sound
    def out(self):
        self.sound.play()

class UgmModalBlinkingEngine(UgmBlinkingEngine):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh.
    Can be used to evoke P300 of different modalities 
    (visual, haptic, auditory, combinations).
    """
    def __init__(self, p_config_manager, p_connection,
                 context=ctx.get_dummy_context('UgmBlinkingEngine'),
                 modalities=['visual',]):
        """Store config manager.
        Args:
            Modalities: modalities used for stimulation, list of strings.
                        available options: 'visual', 'auditory', 'haptic'
        """
        
        super(UgmModalBlinkingEngine, self).__init__(p_config_manager,
                                                     p_connection,
                                                     context)
        self.visual = 'visual' in modalities
        self.haptic = 'haptic' in modalities
        self.auditory = 'auditory' in modalities
        
        #must be here or else they connect to parent class methods
        #~ self._blink_timer = QtCore.QTimer(self)
        #~ self._blink_timer.setSingleShot(True)
        #~ self._blink_timer.connect(self._blink_timer, QtCore.SIGNAL("timeout()"), self._blink)

        #~ self._unblink_timer = QtCore.QTimer(self)
        #~ self._unblink_timer.setSingleShot(True)
        #~ self._unblink_timer.connect(self._unblink_timer, QtCore.SIGNAL("timeout()"), self._unblink)

        #~ self._stop_timer = QtCore.QTimer(self)
        #~ self._stop_timer.setSingleShot(True)
        #~ self._stop_timer.connect(self._stop_timer, QtCore.SIGNAL("timeout()"), self._stop)

        
    def initpyo(self, soundfiles):
        self.context['logger'].info('initialising pyo audio backend')
        try:
            import pyo
        except ImportError:
            print ('ERROR no sound library.\n\t\t Installl pyo!\n\t\tsudo apt-get install python-pyo')
            sys.exit(1)
        self.audio_server = pyo.Server(audio='pa')
        self.audio_server.boot()
        while not self.audio_server.getIsBooted():
            time.sleep(1)
            self.context['logger'].info('audio server bootup'+str(self.audio_server.getIsBooted()))
            self.audio_server.boot()
        self.audio_server.start()
        while not self.audio_server.getIsStarted():
            time.sleep(1)
            self.audio_server.start()
            time.sleep(2)
        sounds = [pyo.SfPlayer(os.path.expanduser(f)) for f in soundfiles]
        assert len(soundfiles) == len(self._active_ids)
        assert len(sounds) == len(self._active_ids)
        self._sounds = dict(zip(self._active_ids, sounds))
        
    def initpygame(self, soundfiles, pygame_buffor):
        self.context['logger'].info('initialising pygame audio backend')
    
        try:
            import pygame
        except ImportError:
            print ('ERROR no sound library.\n\t\t Installl pygame!\n\t\tsudo apt-get install python-pygame')
            sys.exit(1)
        
        pygame.mixer.init(44100, -16, 2, pygame_buffor)
        sounds = [pygame.mixer.Sound(os.path.expanduser(f)) for f in soundfiles]
        soundscompat = [pygameSoundCompat(i) for i in sounds]
        assert len(soundfiles) == len(self._active_ids)
        assert len(sounds) == len(self._active_ids)
        self._sounds = dict(zip(self._active_ids, soundscompat))
    
    
    def _init_auditory(self, configs):
        
        soundfiles = configs.get_param('soundfiles').split(';')
        self.soundbackend = configs.get_param('soundbackend')
        pygame_buffor = int(configs.get_param('pygamebuffor'))
        if self.soundbackend == 'pyo':
            self.initpyo(soundfiles)
        elif self.soundbackend == 'pygame':
            self.initpygame(soundfiles, pygame_buffor)
        self.context['logger'].info('soundfiles: {}'.format(soundfiles))
    
    def _init_haptic(self, configs):
        ids = configs.get_param("haptic_device").split(":")
        vid, pid = [int(i, base=16) for i in ids]
        self.stimulator = HapticStimulator(vid, pid)
        channel_map = (int(i) for i in configs.get_param('haptic_channels_map').split(';'))
        self._haptic_map = dict(zip(self._active_ids, channel_map))
        self._haptic_duration = float(configs.get_param('haptic_duration'))
        
    def _schedule_blink(self, start_time):
        '''Schedule the next blink with possibility of "half blink"'''
        
        #do halfblinks sometimes
        if random.random()<self._global_target_proba:
            self._curr_blink_id = self.id_mgr.get_id()
        else:
            self._curr_blink_id = None
        self._curr_blink_ugm = self.ugm_mgr.get_blink_ugm(self._curr_blink_id)
        self._curr_unblink_ugm = self.ugm_mgr.get_unblink_ugm(self._curr_blink_id)
        curr_time = self.time_mgr.get_time()
        t = 1000*(curr_time - (time.time()-start_time))
        if t < 0:
            t = 0.0
            self.context['logger'].warning("BLINKER WARNING: time between blinks to short for that computer ...")
        self._blink_timer.start(t)
        
    def _timer_on_run(self):
        super(UgmBlinkingEngine, self)._timer_on_run()
        self._blink_timer = QtCore.QTimer(self)
        self._blink_timer.setSingleShot(True)
        self._blink_timer.connect(self._blink_timer, QtCore.SIGNAL("timeout()"), self._blink)

        self._unblink_timer = QtCore.QTimer(self)
        self._unblink_timer.setSingleShot(True)
        self._unblink_timer.connect(self._unblink_timer, QtCore.SIGNAL("timeout()"), self._unblink)

        self._stop_timer = QtCore.QTimer(self)
        self._stop_timer.setSingleShot(True)
        self._stop_timer.connect(self._stop_timer, QtCore.SIGNAL("timeout()"), self._stop)

        self.context['logger'].info('RUN ON START: {}'.format(self._run_on_start))
        if self._run_on_start:
            self.start_blinking()
    
    def set_configs(self, configs):
        for m in self.mgrs:
            m.set_configs(configs)
        self._active_ids = [int(i) for i in configs.get_param('active_field_ids').split(';')]
        self._blink_duration = float(configs.get_param('blink_duration'))
        if self.auditory:
            self._init_auditory(configs)
        if self.haptic:
            self._init_haptic(configs)
        self._run_on_start = int(configs.get_param('running_on_start'))
        self._global_target_proba =  float(configs.get_param('global_target_proba'))
        self._send_halfblinks=int(configs.get_param('send_halfblinks'))
    
                            
    def _blink(self):
        '''Do blinking of configured modality'''
        start_time = time.time()
        
        if self.visual:
            self.update_from(self._curr_blink_ugm)
        update_time = time.time()
        #only visual supports half blinks
        if self._curr_blink_id is not None:
            curr_blink_global_id = self._active_ids[self._curr_blink_id]
            if self.auditory:
                self._sounds[curr_blink_global_id].out()
            if self.haptic:
                self.stimulator.stimulate(
                                self._haptic_map[curr_blink_global_id],
                                self._haptic_duration)
            #half blinks doesnt count to blinks count
            if self._blinks_count >= 0:
                self._blinks_count -= 1
            #and half blinks don't need to be sent
            self.connection.send_blink(self._curr_blink_id, update_time)
        elif self._send_halfblinks:
            self.connection.send_blink(HALFBLINKID, update_time)
            
        t = 1000*(self._blink_duration - (time.time() - start_time))
        if t < 0:
            t = 0.0
            self.context['logger'].warning("BLINKER WARNING: blink duration to short for that computer ...")
        self._unblink_timer.start(t)


    def _unblink(self):
        start_time = time.time()
        if self.visual:
            self.update_from(self._curr_unblink_ugm)
        update_time = time.time()
        if self._blinks_count == 0 or self.STOP:
            self.STOP = False
            curr_time = self.time_mgr.get_time()
            for m in self.mgrs:
                m.reset()
            self._stop_timer.start(1000*(curr_time - (time.time()-start_time)))
        else:
            self._schedule_blink(start_time)
            

if __name__ == '__main__':
    ugm_engine.run()

