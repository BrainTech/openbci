#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus

class Player(object):
    def __init__(self):
        session_bus = dbus.SessionBus()
        player = session_bus.get_object('org.mpris.clementine', '/Player')
        self.iface = dbus.Interface(player, dbus_interface='org.freedesktop.MediaPlayer')
        self.iface.VolumeSet(80)

    def play(self):
        self.iface.Play()