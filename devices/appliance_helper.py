#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from obci.configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types

def send_stop(conn):
    msg = variables_pb2.Variable()
    msg.key = 'stop'
    msg.value = ''
    conn.send_message(message=msg.SerializeToString(), 
                      type=types.DIODE_CONTROL_MESSAGE,
                      flush=True)

def send_start(conn):
    msg = variables_pb2.Variable()
    msg.key = 'start'
    msg.value = ''
    conn.send_message(message=msg.SerializeToString(), 
                      type=types.DIODE_CONTROL_MESSAGE,
                      flush=True)

def send_freqs(conn, freqs):
    msg = variables_pb2.Variable()
    msg.key = 'update'
    msg.value = ';'.join(freqs)
    conn.send_message(message=msg.SerializeToString(), 
                      type=types.DIODE_CONTROL_MESSAGE,
                      flush=True)

    
