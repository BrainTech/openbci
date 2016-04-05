#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
from obci.configs import settings
from obci.acquisition import acquisition_helper

import pygame.mixer
pygame.mixer.init()
pygame.init()  


class Player(object):
    def __init__(self, file_name='Enter.wav'):
        dir_name = os.path.join(settings.MAIN_DIR, 'utils/tagger_gui/sounds')
    	sound_file = acquisition_helper.get_file_path(dir_name, file_name)
        self.sound = pygame.mixer.Sound(sound_file)

    def play(self):
        self.sound.play()
