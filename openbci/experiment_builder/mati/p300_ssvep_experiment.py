#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, subprocess, time, random
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
from multiplexer.clients import connect_client
import variables_pb2, settings, configurer
import pygame
pygame.init()

from ugm.ugm_config_manager import UgmConfigManager
from openbci.experiment_builder import experiment_logging
from openbci.experiment_builder import keystroke
LOGGER = experiment_logging.get_logger('p300_SSVEP_EXPERIMENT', 'info')
from openbci.tags import tagger
TAGGER = tagger.get_tagger()

# time (in secs) of a single trial of ssvep block
SSVEP_TRIAL_TIME = 2
BREAK_TIME = 5
TASK_TIME = 2
BASELINE_TIME = 2

SSVEP_FREQS = [10, 15]
SOUND_FILE='sound.wav'

FREQS = [0]*8
FREQ_ID = 1

SPACE_KEY_CODE = str(32)

INSTRUCTIONS_BEFORE_BLOCK = ["RAZ\nDwa\nDupa dupa dupa", "Dupa dupa dupa \nDWA"]
INSTRUCTIONS_AFTER_BLOCK = ["TRZY"]
TRIAL_SCREEN_FILE = 'p300_ssvep'
TEXT_SCREEN_FILE = 'text_neg'
STIM_TYPES = ['p300', 'ssvep', 'p300_ssvep']

# type of subsequent blocks
BLOCKS = [
          {'type':'mixed',
           'size':3,
           'instructions_before_block':INSTRUCTIONS_BEFORE_BLOCK,
           'instructions_after_block':INSTRUCTIONS_AFTER_BLOCK,
           },
          {'type':'mixed',
           'size':3,
           'instructions_before_block':INSTRUCTIONS_BEFORE_BLOCK,
           'instructions_after_block':INSTRUCTIONS_AFTER_BLOCK,
           },
          {'type':'mixed',
           'size':3,
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

def wait_for_space():
  LOGGER.info("Start waiting for space")
  keystroke.wait([SPACE_KEY_CODE])
  LOGGER.info("Got space!")

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
  for i in range(BREAK_TIME):
    send_text_screen("Mrugaj teraz. Odliczanie "+str(5-i))
    time.sleep(1)
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

def perform_intro():
  send_text_screen(u"Hej koleżko\njeden\ndwa\ntrzy\ncztery\npięć")
  wait_for_space()

  send_text_screen(u"Hej hop\nco tuaj ąęćg")
  wait_for_space()

  for i in range(BREAK_TIME):
    send_text_screen(u"Przygotuj się do baseline. Odliczanie "+str(5-i))
    time.sleep(1)
  send_text_screen(u"Patrz się po prostu")
  time.sleep(BASELINE_TIME)

  send_text_screen(u"Teraz drugi baseline")
  wait_for_space()

  for i in range(BREAK_TIME):
    send_text_screen(u"Przygotuj się do baseline.\nZamknij oczy i otwórz na dźwięk.\nOdliczanie "+str(5-i))
    time.sleep(1)

  send_text_screen(u"Zamknij oczy")
  time.sleep(BASELINE_TIME)
  play_sound(SOUND_FILE)

  send_text_screen(u"Teraz będzie badanie")
  wait_for_space()



def run():
  #perform_intro()
  for b in BLOCKS:
    for i in b['instructions_before_block']:
      send_text_screen(i)
      wait_for_space()
    t = time.time()

    TAGGER.send_tag(t, t, "task_start", {})
    run_program_for('gnome-breakout', TASK_TIME)
    TAGGER.send_tag(t, t, "task_end", {})

    for i in b['instructions_after_block']:
      send_text_screen(i)
      wait_for_space()
    t = time.time()
    TAGGER.send_tag(t, t, "block_start",
                    {
        "size" : b['size'],
        "type" : b['type'],
        })

    for i in range(b['size']):
      perform_trial_break()
      send_screen(TRIAL_SCREEN_MGR.config_to_message())
      stim_type = b['type']
      if stim_type == 'mixed':
        stim_type = STIM_TYPES[random.randint(0, len(STIM_TYPES)-1)]
      LOGGER.info("STIM TYPE: "+stim_type)
      t1 = time.time()
      freq = -1
      if stim_type == 'ssvep':
        freq = SSVEP_FREQS[random.randint(0, len(SSVEP_FREQS)-1)]
        update_diode_freq(freq)
        time.sleep(SSVEP_TRIAL_TIME)
        update_diode_freq(0)
      elif stim_type == 'p300':
        send_start_blinking()
        wait_for_blinking_stopped()
      elif stim_type == 'p300_ssvep':
        freq = SSVEP_FREQS[random.randint(0, len(SSVEP_FREQS)-1)]
        update_diode_freq(freq)
        send_start_blinking()
        wait_for_blinking_stopped()
        update_diode_freq(0)
      else:
        raise Exception("Unrecognised stim type "+str(stim_type))
      t2 = time.time()
      TAGGER.send_tag(t1, t2, "trial_"+stim_type,
                      {
          "type" : stim_type,
          "freq" : str(freq),
          })

    TAGGER.send_tag(t, t, "block_end",
                    {
        "size" : b['size'],
        "type" : b['type'],
        })

  send_text_screen("DZIEKI")
  wait_for_space()


if __name__ == '__main__':
  run()
