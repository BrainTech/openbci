#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from gui.ugm import ugm_config_manager

TEXT_SCREEN_MGR = ugm_config_manager.UgmConfigManager('text_neg')
TEXT_ID = 101

def send_text(conn, text):
  cfg = TEXT_SCREEN_MGR.get_config_for(TEXT_ID)
  cfg['message'] = text
  TEXT_SCREEN_MGR.set_config(cfg)
  send_config(conn, TEXT_SCREEN_MGR.config_to_message())

def send_config(conn, config, type=0):
  l_type = type
  l_msg = variables_pb2.UgmUpdate()
  l_msg.type = int(l_type)
  l_msg.value = config
  conn.send_message(
    message = l_msg.SerializeToString(), 
    type=types.UGM_UPDATE_MESSAGE, flush=True)

def send_start_blinking(conn):
    msg = variables_pb2.Variable()
    msg.key = 'start_blinking'
    msg.value = ''
    conn.send_message(message=msg.SerializeToString(), 
                      type=types.UGM_CONTROL_MESSAGE,
                      flush=True)

