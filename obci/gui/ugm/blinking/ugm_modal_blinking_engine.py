#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
# Marian Dovgialo <marian.dowgialo@gmail.com>

# requires pyo for sound
from __future__ import print_function
from ugm_blinking_engine import UgmBlinkingEngine
try:
    import pyo
except ImportError:
    print ('ERROR no sound library.\n\t\t Installl pyo!\n\t\tsudo apt-get install python-pyo')
from obci.devices.haptics.HapticsControl import HapticStimulator
from obci.utils import context as ctx
from obci.gui.ugm import ugm_engine
from PyQt4 import QtCore
import time


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
        self._blink_timer = QtCore.QTimer(self)
        self._blink_timer.setSingleShot(True)
        self._blink_timer.connect(self._blink_timer, QtCore.SIGNAL("timeout()"), self._blink)

        self._unblink_timer = QtCore.QTimer(self)
        self._unblink_timer.setSingleShot(True)
        self._unblink_timer.connect(self._unblink_timer, QtCore.SIGNAL("timeout()"), self._unblink)

        self._stop_timer = QtCore.QTimer(self)
        self._stop_timer.setSingleShot(True)
        self._stop_timer.connect(self._stop_timer, QtCore.SIGNAL("timeout()"), self._stop)


        if self._run_on_start:
            self.start_blinking()
        
    def _init_auditory(self, configs):
        soundfiles = configs.get_param('soundfiles').split(';')
        self.audio_server = pyo.Server()
        self.audio_server.boot()
        self.audio_server.start()
        sounds = [pyo.SfPlayer(f) for f in soundfiles]
        assert len(soundfiles) == len(self._active_ids)
        assert len(sounds) == len(self._active_ids)
        self._sounds = dict(zip(self._active_ids, sounds))
    
    def _init_haptic(self, configs):
        ids = configs.get_param("haptic_device").split(":")
        vid, pid = [int(i, base=16) for i in ids]
        self.stimulator = HapticStimulator(vid, pid)
        channel_map = (int(i) for i in configs.get_param('haptic_channels_map').split(';'))
        self._haptic_map = dict(zip(self._active_ids, channel_map))
        self._haptic_duration = float(configs.get_param('haptic_duration'))
        
    
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
    
                            
    def _blink(self):
        '''Do blinking of configured modality'''
        start_time = time.time()
        curr_blink_global_id = self._active_ids[self._curr_blink_id]
        if self.visual:
            self.update_from(self._curr_blink_ugm)
        update_time = time.time()
        if self.auditory:
            self._sounds[curr_blink_global_id].out()
        if self.haptic:
            self.stimulator.stimulate(
                            self._haptic_map[curr_blink_global_id],
                            self._haptic_duration)
        
        if self._blinks_count >= 0:
            self._blinks_count -= 1
        self.connection.send_blink(self._curr_blink_id, update_time)
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

