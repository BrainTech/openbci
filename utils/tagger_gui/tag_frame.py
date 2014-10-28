#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from timer import Timer
from button import Button
from frame import Frame
from player import Player
import time 

class TagFrame(Frame):
    def __init__(self):
        super(TagFrame, self).__init__()

    def init_frame(self, status_bar, tag_signal, params):
        self.status_bar = status_bar
        self.tag_signal = tag_signal
        self.tags = []
        self.tag = params['tag_start_name']
        self.duration = int(params['duration'])
        self.tag_on_end = params['tag_on_end']
        self.sound = params['sound']
        self.repetitions_number = 0
        self.is_first = 0
        self.tag_signal = tag_signal
        
        if params['sound']:
            self.sound = 1
            self.player = Player()
        else:
            self.sound=0

        if self.duration:
            self.timer = Timer(self.duration, self)
            self.timer.set_position(2)
            if self.tag_on_end  != '':
                self.timer.set_stop_action(self.action_stop)

            self.stop_button = Button('stop', self)
            self.stop_button.set_position(3)
            self.stop_button.connect(self.action_stop)
            self.stop_button.set_disable()
        elif self.tag_on_end  != '':
            self.stop_button = Button('stop', self)
            self.stop_button.set_position(3)
            self.stop_button.connect(self.action_stop)
            self.stop_button.set_disable()

        self.start_button = Button(self.tag, self)
        self.start_button.set_position(1)
        self.start_button.connect(self.action_start)
        self.clear_button=Button('clear', self)
        self.clear_button.set_position(4)
        self.clear_button.connect(self.action_clear)

        self.set_off()

    def _create_tag(self, tag):
        self.tags.append({'timestamp':str(time.time()), 'name':str(tag)})

    def _create_status_bar_message(self, type_, tag):
        if type_ == 'create':
            return "Tag: {} was create.".format(tag)
        else:
            names = [name for name in [t['name'] for t in tag]]
            if type_ == 'delete':
                if len(names) == 1:
                    return "Tag: {} was delete.".format(''.join(names))
                else:
                    return "Tags: {} were delate.".format(', '.join(names))
            elif type_ == 'send':
                if len(names) == 1:
                    return "Tag: {} was send.".format(''.join(names))
                else:
                    return "Tags: {} were send.".format(', '.join(names))

    def action_start(self):
        if self.sound:
            self.player.play()
        if (not self.repetitions_number) and (not self.is_first):
            self.finish_action_elier_frame()
        self.start_button.set_disable()
        self._create_tag(self.tag)
        self.status_bar.show_message(self._create_status_bar_message('create', self.tag))

        if self.duration:
            self.stop_button.set_enable()
            self.timer.clock_start()
        elif self.tag_on_end  != '':
            self.stop_button.set_enable()
        else:
            self.active_next_frame()

    def action_stop(self):
        if self.sound:
            self.player.play()

        if self.duration and self.timer.is_on:
            self.timer.clock_stop()

        if self.tag_on_end != '':
            self._create_tag(self.tag_on_end)
            self.status_bar.show_message(self._create_status_bar_message('create', self.tag_on_end))
        
        self.stop_button.set_disable()
        self.active_next_frame()

    def _update_repetition(self):
        self.repetitions_number+=1

    def action_clear(self):
        self.status_bar.show_message(self._create_status_bar_message('delete', self.tags))
        self.tags = []
        self.set_on()
        self.deactivation_next_frame()
        if self.duration:
            self.timer.clock_reset()
        self._update_repetition()

    def set_on(self):
        self.start_button.set_enable()
        if self.duration:
            self.timer.clock_reset()
            self.stop_button.set_enable()
        self.clear_button.set_enable()
        self.set_is_on()

    def set_off(self):
        self.clear_button.set_disable()
        if self.duration:
            self.stop_button.set_disable()
        self.start_button.set_disable()
        self.set_is_off()

    def _send_tags(self):
        for tag in self.tags:
            self.tag_signal.emit(str(tag))
        self.tags = []

    def finish_frame_action(self):
        self.status_bar.show_message(self._create_status_bar_message('send', self.tags))
        self._send_tags()
        self.set_off()
        self.next_frame.remove(self.next_frame[0])
        if self.is_first:
            self.is_first=0
        print self, self.next_frame