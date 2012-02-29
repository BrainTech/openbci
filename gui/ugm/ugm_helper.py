#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from configs import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from gui.ugm import ugm_config_manager

TEXT_SCREEN_MGR = ugm_config_manager.UgmConfigManager('text_neg')
TEXT_ID = 101
STATUS_ID = 54321

def send_text(conn, text):
  cfg = TEXT_SCREEN_MGR.get_config_for(TEXT_ID)
  cfg['message'] = text
  TEXT_SCREEN_MGR.set_config(cfg)
  send_config(conn, TEXT_SCREEN_MGR.config_to_message())

def send_status(conn, text):
  send_config_for(conn, STATUS_ID, 'message', text)

def send_config_for(conn, id, key, value):
  config = str([{'id':id,
             key:value}])
  send_config(conn, config, 1)

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




class UgmColorUpdater(object):
  def __init__(self, ugm_config, ids, color='g'):
    assert(color in ['r', 'g', 'b'])
    self.color = color
    self.mutable_configs = []
    self.initial_configs = []
    mgr = ugm_config_manager.UgmConfigManager(ugm_config)
    for id in ids:
      self.initial_configs.append(
        {'id':id,
         'color':mgr.get_config_for(id)['color']
         })
      self.mutable_configs.append(
        {'id':id,
         'color':mgr.get_config_for(id)['color']
         })
  
  def update(self, ind, level):
    if self.color == 'g':
      self.mutable_configs[ind]['color'] = '#%02x%02x%02x' % (255 - int(255*level), 255, 255 - int(255*level))
    elif self.color == 'r':
      self.mutable_configs[ind]['color'] = '#%02x%02x%02x' % 255, (255 - int(255*level), 255 - int(255*level))
    elif self.color == 'b':
      self.mutable_configs[ind]['color'] = '#%02x%02x%02x' % (255 - int(255*level), 255 - int(255*level)), 255

    return self.mutable_configs[ind]

  def update_ugm(self, ind, level):
    if level == -1:
      return str([self.initial_configs[ind]])
    else:
      return str([self.update(ind, level)])

  
    
      
    

    
