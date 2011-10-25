#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, subprocess, time, random
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
from multiplexer.clients import connect_client
import variables_pb2, settings, configurer
import pygame
from ugm.ugm_config_manager import UgmConfigManager
from openbci.experiment_builder import experiment_logging
LOGGER = experiment_logging.get_logger('p300_SSVEP_EXPERIMENT', 'info')

# time (in secs) of a single trial of ssvep block
SSVEP_TRIAL_TIME = 2
SSVEP_FREQS = [10, 15]
TASK_TIME = 2
SOUND_FILE='sound.wav'

FREQS = [0]*8
FREQ_ID = 1

INSTRUCTIONS_BEFORE_BLOCK = []
INSTRUCTIONS_AFTER_BLOCK = []
TRIAL_SCREEN_FILE = 'p300_ssvep'
TEXT_SCREEN_FILE = 'text'

# type of subsequent blocks
BLOCKS = [
          {'type':'p300',
           'size':5,
           'instructions_before_block':INSTRUCTIONS_BEFORE_BLOCK,
           'instructions_after_block':INSTRUCTIONS_AFTER_BLOCK,
           },
          {'type':'ssvep',
           'size':5,
           'instructions_before_block':INSTRUCTIONS_BEFORE_BLOCK,
           'instructions_after_block':INSTRUCTIONS_AFTER_BLOCK,
           },
          {'type':'ssvep_p300',
           'size':5,
           'instructions_before_block':INSTRUCTIONS_BEFORE_BLOCK,
           'instructions_after_block':INSTRUCTIONS_AFTER_BLOCK,
           }
          ]

CONFIGURER = configurer.Configurer(settings.MULTIPLEXER_ADDRESSES)
CONFIGURER.get_configs([
    'PEER_READY'+str(peers.UGM), 
    'PEER_READY'+str(peers.AMPLIFIER), 
    #'PEER_READY'+str(peers.BLINK_AND_DIODE_CATCHER), 
])

CONNECTION = connect_client(type = peers.LOGIC)
TRIAL_SCREEN_MGR = UgmConfigManager(TRIAL_SCREEN_FILE)
TEXT_SCREEN_MGR = UgmConfigManager(TEXT_SCREEN_FILE)
TEXT_ID = 101




def run_program_for(program, t):
  LOGGER.info("Run program: "+program)
  game = subprocess.Popen([program, ""])
  time.sleep(t)
  game.kill()
  LOGGER.info("Killed the program")

def send_text_screen(text):
  LOGGER.info("Send text screen: "+text)
  cfg = TEXT_SCREEN_MGR.get_config_for(TEXT_ID)
  cfg['message'] = text
  TEXT_SCREEN_MGR.set_config(cfg)
  send_screen(TEXT_SCREEN_MGR.config_to_message())
  LOGGER.info("Text screen sent")

def send_screen(screen):
  LOGGER.info("Send screen!")
  LOGGER.debug(screen)
  l_type = 0
  l_msg = variables_pb2.UgmUpdate()
  l_msg.type = int(l_type)
  l_msg.value = screen
  CONNECTION.send_message(
    message = l_msg.SerializeToString(), 
    type=types.UGM_UPDATE_MESSAGE, flush=True)
  LOGGER.info("Screen sent")

def update_diode_freq(freq):
  LOGGER.info("Update diode with: "+str(freq))
  freqs = list(FREQS)
  freqs[FREQ_ID] = freq
  freqs_str = " ".join(['%s' % i for i in freqs])
  l_msg = variables_pb2.Variable()
  l_msg.key = "Freqs"
  l_msg.value = freqs_str
  CONNECTION.send_message(
    message = l_msg.SerializeToString(), 
    type=types.DIODE_UPDATE_MESSAGE, flush=True)
  LOGGER.info("Diode sent")
    
def play_sound(f):
  LOGGER.info("Play sound from: "+str(f))
  pygame.mixer.Sound(f).play()

def perform_trial_break():
  LOGGER.info("Start trial break")
  for i in range(5):
    send_text_screen("Mrugaj "+str(5-i))
    time.sleep(1) #keyboard
  LOGGER.info("End trial break")

def send_start_blinking():
  LOGGER.info("Send start blinking message")
  l_msg = variables_pb2.Variable()
  l_msg.key = "start_blinking"
  l_msg.value = ""
  CONNECTION.send_message(
    message = l_msg.SerializeToString(), 
    type=types.UGM_CONTROL_MESSAGE, flush=True)
  LOGGER.info("Start blinking message sent")

class Waiter(BaseMultiplexerServer):
  def __init__(self, addresses):
    super(Waiter, self).__init__(addresses=addresses, type=peers.EXPERIMENT_MANAGER)
  def handle_message(self, mxmsg):
    if mxmsg.type == types.UGM_ENGINE_MESSAGE:
      m = variables_pb2.Variable()
      m.ParseFromString(mxmsg.message)
      if m.key == 'blinking_stopped':
        self.close()
        self.working = False
    self.no_response()
def wait_for_blinking_stopped():
  LOGGER.info("Start waiting for blinking_stopped")
  Waiter(settings.MULTIPLEXER_ADDRESSES).loop()
  LOGGER.info("Waiting for blinking_stopped finished")


# upewnij sie ze hashtable jest takie jakie trzeba

"""for i in wstepne instrukcje:
  wyslij instrukcje
  przechwyc spacje

wyslij instrukcje z odliczaniem i info ze zaraz baseline
wyslij instrukcje zamknij oczy
wyslij sygnal dzwiekowy po 30 s
wyslij instukcje z odliczaniem i info ze zaraz baseline
wyslij instrukcje zamknij oczy
wyslij sygnal dzwiekowy po 30 s
play_sound(SOUND_FILE)
wyslij instukcje z odliczaniem i info ze zaraz baseline"""






def run():
  for b in BLOCKS:
    for i in b['instructions_before_block']:
      pass
        #wyslij instrukcje
        #przechwyc spacje

    run_program_for('gnome-breakout', TASK_TIME)

    for i in b['instructions_after_block']:
      pass
      #wyslij instrukcje
      #przechwyc spacje


    for i in range(b['size']):
      send_screen(TRIAL_SCREEN_MGR.config_to_message())
      if b['type'] == 'ssvep':
        freq = SSVEP_FREQS[random.randint(0, len(SSVEP_FREQS)-1)]
        update_diode_freq(freq)
        time.sleep(SSVEP_TRIAL_TIME)
        update_diode_freq(0)
      elif b['type'] == 'p300':
        send_start_blinking()
        wait_for_blinking_stopped()
      elif b['type'] == 'p300_ssvep':
        freq = SSVEP_FREQS[random.randint(0, len(SSVEP_FREQS)-1)]
        update_diode_freq(freq)
        send_start_blinking()
        wait_for_blinking_stopped()
        update_diode_freq(0)

      perform_trial_break()

if __name__ == '__main__':
  run()
