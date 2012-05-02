#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types


def diode_stop(conn):
  l_msg = variables_pb2.Variable()
  l_msg.key = 'stop'
  l_msg.value = ''
  conn.send_message(
      message = l_msg.SerializeToString(), 
      type=  types.DIODE_CONTROL_MESSAGE, flush=True)
    
