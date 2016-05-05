#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import time
from PyQt4 import QtCore

from obci.gui.ugm import ugm_engine
import ugm_blinking_time_manager
import ugm_blinking_id_manager
import ugm_blinking_count_manager
import ugm_blinking_ugm_manager
from obci.utils import context as ctx

from PyQt4 import QtCore
class UgmBlinkingEngine(ugm_engine.UgmEngine):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh."""
    def __init__(self, p_config_manager, p_connection, context=ctx.get_dummy_context('UgmBlinkingEngine')):
        """Store config manager."""
        super(UgmBlinkingEngine, self).__init__(p_config_manager, p_connection, context)
        self.time_mgr = ugm_blinking_time_manager.UgmBlinkingTimeManager()
        self.id_mgr = ugm_blinking_id_manager.UgmBlinkingIdManager()
        self.ugm_mgr = ugm_blinking_ugm_manager.UgmBlinkingUgmManager()
        self.count_mgr = ugm_blinking_count_manager.UgmBlinkingCountManager()

        self.mgrs = [self.time_mgr, self.id_mgr, self.ugm_mgr, self.count_mgr]
        self.STOP = False
        self._run_on_start = False
        
    def set_configs(self, configs):
        for m in self.mgrs:
            m.set_configs(configs)
        self._blink_duration = float(configs.get_param('blink_duration'))
        self._run_on_start = int(configs.get_param('running_on_start'))
        assert(self._blink_duration > 0)

    def control(self, msg):
        super(UgmBlinkingEngine, self).control(msg)
        msg_type = msg.key
        if msg_type == 'start_blinking':
            self.start_blinking()
        elif msg_type == 'stop_blinking':
            self.stop_blinking()
        #elif msg_type == 'update_and_start_blinking':
        #    self._update_and_start_blinking()
        else:
            raise Exception("Got ugm_control unrecognised msg_type:"+msg_type)

    #def _update_and_start_blinking(self):
    #    for m in self.mgrs:
    #        m.reset()
    #    requested_configs = self.get_requested_configs()
    #    configs = self.connection.get_configs(requested_configs)
    #    self.set_configs(configs)
    #    self.start_blinking()

    def start_blinking(self):
        self._blinks_count = self.count_mgr.get_count()
        self._schedule_blink(time.time())
        self.connection.send_blinking_started()

    def _schedule_blink(self, start_time):
        self._curr_blink_id = self.id_mgr.get_id()
        self._curr_blink_ugm = self.ugm_mgr.get_blink_ugm(self._curr_blink_id)
        self._curr_unblink_ugm = self.ugm_mgr.get_unblink_ugm(self._curr_blink_id)
        curr_time = self.time_mgr.get_time() #time if next blink I guess?
        t = 1000*(curr_time - (time.time()-start_time))
        if t < 0:
            t = 0.0
            self.context['logger'].warning("BLINKER WARNING: time between blinks to short for that computer ...")
        self._blink_timer.start(t)

    def stop_blinking(self):
        self.STOP = True

    def _blink(self):
        start_time = time.time()
        self.update_from(self._curr_blink_ugm)
        update_time = time.time()
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

    def _stop(self):
        self.connection.send_blinking_stopped()

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


        if self._run_on_start:
            self.start_blinking()
			
if __name__ == '__main__':
	ugm_engine.run()

