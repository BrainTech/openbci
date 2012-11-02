#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
import time

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
from obci_configs import variables_pb2
from obci_utils import context as ctx
from gui import gui_logging as logger

class UgmBlinkingConnection(object):
    """Provides connection for engine to 'external' wold - other MX modules."""
    def __init__(self, addresses,context=ctx.get_dummy_context('UgmBlinkingConnection')):
        self.connection = connect_client(type = peers.UGM_ENGINE, addresses=addresses)
        self.context = context
        self.blink_msg = variables_pb2.Blink()

    def send_blink(self, blink_id, blink_time):
        self.blink_msg.index = blink_id
        self.blink_msg.timestamp = blink_time
        self.connection.send_message(message = self.blink_msg.SerializeToString(), type = types.BLINK_MESSAGE, flush=True)

    def send_blinking_started(self):
        self.context['logger'].debug("Send blink started")
        msg = variables_pb2.Variable()
        msg.key = "blinking_started"
        msg.value = str(time.time())
        self.connection.send_message(message = msg.SerializeToString(), type = types.UGM_ENGINE_MESSAGE, flush=True)

    def send_blinking_stopped(self):
        self.context['logger'].debug("Send blinking stopped")
        msg = variables_pb2.Variable()
        msg.key = "blinking_stopped"
        msg.value = str(time.time())
        self.connection.send_message(message = msg.SerializeToString(), type = types.UGM_ENGINE_MESSAGE, flush=True)

    def send_mouse_event(self, button_nr):
        self.context['logger'].debug("Send mouse event "+str(button_nr))
        msg = variables_pb2.Variable()
        msg.key = "mouse_event"
        msg.value = str(button_nr)
        self.connection.send_message(message = msg.SerializeToString(), type = types.UGM_ENGINE_MESSAGE, flush=True)

    def send_keyboard_event(self, key):
        self.context['logger'].debug("Send keyboard event "+str(key))
        msg = variables_pb2.Variable()
        msg.key = "keybord_event"
        msg.value = str(key)
        self.connection.send_message(message = msg.SerializeToString(), type = types.UGM_ENGINE_MESSAGE, flush=True)

        


