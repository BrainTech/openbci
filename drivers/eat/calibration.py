#-*- coding: utf-8 -*-

"""
TODO: add some notification when searching for eyetrackers
TODO: get rid of time.sleep
TODO: add animation (moving & shrinking)
TODO: remove logic from connector and view and put it in CalibrationLogic
TODO: remove communication from view and put it in connector
TODO: proper logging messages
"""

import signal
import sys

#from tobii import eye_tracking_io
#import tobii.eye_tracking_io.eyetracker
#import tobii.eye_tracking_io.mainloop
#import tobii.eye_tracking_io.browsing
#import tobii.eye_tracking_io.types

import eye_tracking_io.eyetracker
import eye_tracking_io.mainloop
import eye_tracking_io.browsing
import eye_tracking_io.types

from obci.control.peer.configured_client import ConfiguredClient
from multiplexer import multiplexer_constants
from obci.configs import settings
import logging
import threading
import random
import os.path
import glob
import time
import pygame.display
import pygame.event


class EatException(Exception):
    pass

class EtrCalibrationTobii(ConfiguredClient):
    """
    MX peer which performs Tobii eyetracker calibration.
    """
    def __init__(self, addresses):
        super(EtrCalibrationTobii, self).__init__(addresses=addresses, type=multiplexer_constants.peers.CLIENT)
        self.logger.info("Starting EAT calibration...")
        self._init_signals()
        self.ready()

    def _init_signals(self):
        self.logger.info("Signal handler setup")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())

    def signal_handler(self):
        def handler(signum, _frame):
            self.logger.info("Got signal " + str(signum) + ": terminating")
            sys.exit(-signum)
        return handler

    def run(self):
        CalibrationLogic().run()
        sys.exit(0)


class CalibrationLogic(object):
    def __init__(self):
        self.connector = CalibrationConnector()
        self.view = CalibrationView()
        self.points = [(0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9), (0.5, 0.5)]
        random.shuffle(self.points)
        self.view.set_initial_point(self.points[-1])
    
    def run(self):
        self.view.show_initial_message()
        self.connector.browse()
        self.connector.connect()
        self.view.show_intro_message()
        self.connector.start_calibration()
        for point in self.points:
            self.view.set_point(point)
            self.connector.collect_data(point)
        self.connector.compute()
        self.connector.save_calibration()
        self.view.show_outro_message()
        self.connector.close()


class CalibrationView(object):
    ASPECT_TOLERANCE = 10 ** -3
    SCALE_TIME = 0.8
    MOVE_TIME = 1.5
    
    def __init__(self):
        self.surface = None
        self.w, self.h = (0, 0)
        self.old_point = (0.5, 0.5)
        self.init_display()
        self.default_font = pygame.font.SysFont("Futura, Century Gothic, URW Gothic L, sans", 48)
    
    def init_display(self):
        pygame.display.init()
        pygame.font.init()
        display_mode = self.find_best_mode()
        self.surface = pygame.display.set_mode(display_mode, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
        self.w, self.h = display_mode
        self.anim_speed_init = 1
        self.anim_speed = self.anim_speed_init
        self.anim = glob.glob("fly/fly_*.png")
        self.anim.sort()
        self.anim_pos = 0
        self.anim_max = len(self.anim) - 1
        self.img = pygame.image.load(self.anim[0])
    
    @classmethod
    def find_best_mode(cls):
        """
        Find mode corresponding to native resolution of main screen.
        """
        aspects = [16.0 / 10.0, 16.0 / 9.0, 4.0 / 3.0]
        modes = pygame.display.list_modes()
        for (w, h) in reversed(sorted(modes)):
            a = float(w) / float(h)
            fit = min([abs(a - b) for b in aspects])
            if fit < cls.ASPECT_TOLERANCE:
                return (w, h)
        raise Exception("No acceptable mode found")
    
    def show_initial_message(self):
        self.display_text(u"Łączenie")
        pygame.display.flip()
    
    def show_intro_message(self):
        self.display_text(u"Gotowy do kalibracji [spacja]")
        self.wait_for_continue()
    
    def show_outro_message(self):
        self.display_text(u"Kalibracja zakończona [spacja]")
        self.wait_for_continue()
        pygame.display.quit()
        
    def wait_for_continue(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                return

    def display_text(self, text):
        pygame.draw.rect(self.surface, (0x55, 0x55, 0x55), pygame.Rect(0, 0, self.w, self.h))
        text_surface = self.default_font.render(text, True, (0xaa, 0xaa, 0xaa))
        self.surface.blit(text_surface, ((self.w - text_surface.get_width()) / 2, (self.h - text_surface.get_height()) / 2))
        pygame.display.flip()
        
    def expand_point(self):
        x, y = self.old_point[0] * self.w, self.h * (1.0 - self.old_point[1])
        t0 = time.time()
        t = t0
        while t - t0 < self.SCALE_TIME:
            size = 0.01 + (0.04 * (t - t0)) / self.SCALE_TIME
            #r = self.h * size
            #pygame.draw.rect(self.surface, (0x55, 0x55, 0x55), pygame.Rect(0, 0, self.w, self.h))
            #pygame.draw.ellipse(self.surface, (0x55, 0xff, 0x55), pygame.Rect(x - r, y - r, 2 * r, 2 * r))
            Butterfly = pygame.image.load('fly/fly_1.png').convert()
            Butterfly = pygame.transform.scale(Butterfly, (self.w * size,self.h * size))
            self.surface.blit(Butterfly,(x-self.w * size,y - self.h * size))
            pygame.display.flip()
            t = time.time()
    
    def shrink_point(self):
        x, y = self.old_point[0] * self.w, self.h * (1.0 - self.old_point[1])
        t0 = time.time()
        t = t0
        while t - t0 < self.SCALE_TIME:
            size = 0.05 - (0.04 * (t - t0)) / self.SCALE_TIME
            #r = self.h * size
            #pygame.draw.rect(self.surface, (0x55, 0x55, 0x55), pygame.Rect(0, 0, self.w, self.h))
            #pygame.draw.ellipse(self.surface, (0x55, 0xff, 0x55), pygame.Rect(x - r, y - r, 2 * r, 2 * r))
            Butterfly = pygame.image.load('fly/fly_1.png').convert()
            Butterfly = pygame.transform.scale(Butterfly, (self.w * size,self.h * size))
            self.surface.blit(Butterfly,(x-self.w * size,y - self.h * size))
            pygame.display.flip()
            t = time.time()
        
    def move_point(self, target):
        r = self.h * 0.05
        t0 = time.time()
        t = t0
        while t - t0 < self.MOVE_TIME:
            s = (t - t0) / self.MOVE_TIME
            point = target[0] * s + self.old_point[0] * (1.0 - s), target[1] * s + self.old_point[1] * (1.0 - s)
            x, y = point[0] * self.w, self.h * (1.0 - point[1])
            if self.anim_pos != 0:
                self.anim_speed-=1

            if self.anim_speed == 0:
                self.img = pygame.image.load(self.anim[self.anim_pos])
                self.anim_speed = self.anim_speed_init
                if self.anim_pos >= self.anim_max:
                    self.anim_pos = 0
                    
                else:
                    self.anim_pos+=1

            self.surface.blit(self.img,(x - self.w,y - self.h))
            #pygame.draw.rect(self.surface, (0x55, 0x55, 0x55), pygame.Rect(0, 0, self.w, self.h))
            #pygame.draw.ellipse(self.surface, (0x55, 0xff, 0x55), pygame.Rect(x - r, y - r, 2 * r, 2 * r))
            pygame.display.flip()
            t = time.time()
    
    def set_point(self, point):
        self.expand_point()
        self.move_point(point)
        self.old_point = point
        self.shrink_point()
    
    def set_initial_point(self, point):
        self.old_point = point


class BrowseThread(threading.Thread):
    def __init__(self):
        super(BrowseThread, self).__init__()
        self.mainloop = None
        self.browser = None
        self.eyetracker_info = None
        self.discovery = threading.Condition()
        
    def run(self):
        self.mainloop = eye_tracking_io.mainloop.Mainloop()
        self.browser = eye_tracking_io.browsing.EyetrackerBrowser(self.mainloop, self.browsing_callback)
        self.mainloop.run()
        self.browser.stop()
    
    def browsing_callback(self, _id, msg, eyetracker_info):
        logging.getLogger('eat_amplifier').info(str(msg))
        if msg == 'Found':
            with self.discovery:
                logging.getLogger("eat_amplifier").info("Got eyetracker info: " + str(eyetracker_info))
                self.eyetracker_info = eyetracker_info
                self.discovery.notify()
    
    def kill(self):
        logging.getLogger("eat_amplifier").info("killed")
        if self.browser:
            self.browser.stop()
        if self.mainloop:
            self.mainloop.quit()


class ConnectThread(threading.Thread):
    def __init__(self, eyetracker_info):
        super(ConnectThread, self).__init__()
        self.mainloop = None
        self.eyetracker_info = eyetracker_info
        self.eyetracker = None
        self.established = threading.Condition()
    
    def run(self):
        self.mainloop = eye_tracking_io.mainloop.Mainloop()
        eye_tracking_io.eyetracker.Eyetracker.create_async(self.mainloop, self.eyetracker_info, self.eyetracker_callback)
        self.mainloop.run()
    
    def eyetracker_callback(self, _error, eyetracker):
        with self.established:
            self.eyetracker = eyetracker
            self.established.notify()
        
    def kill(self):
        self.mainloop.quit()


class CalibrationConnector(object):
    def __init__(self):
        self.logger = logging.getLogger("eat_amplifier")
        self.eyetracker_info = None
        self.eyetracker = None
        self.eyetracker_thread = None
        eye_tracking_io.init()
        #self._detect_eyetracker()
        #self._connect_to_eyetracker()
        #self._wait_for_key()

    def browse(self):
        browse_thread = BrowseThread()
        browse_thread.start()
        with browse_thread.discovery:
            browse_thread.discovery.wait(5)
            browse_thread.kill()
            if browse_thread.eyetracker_info:
                self.eyetracker_info = browse_thread.eyetracker_info
                print self.eyetracker_info
            else:
                raise EatException("No eyetracker found")
    
    def connect(self):
        self.eyetracker_thread = ConnectThread(self.eyetracker_info)
        self.eyetracker_thread.start()
        with self.eyetracker_thread.established:
            self.eyetracker_thread.established.wait(5)
            if self.eyetracker_thread.eyetracker:
                self.eyetracker = self.eyetracker_thread.eyetracker
            else:
                raise EatException("Could not connect to eyetracker")
    
    def start_calibration(self):
        self.eyetracker.StartCalibration(None)
    
    def collect_data(self, point):
        self.eyetracker.AddCalibrationPoint(eye_tracking_io.types.Point2D(point[0], point[1]))
        time.sleep(2)
    
    def compute(self):
        self.eyetracker.ComputeCalibration(self.compute_calibration_finished)
    
    def compute_calibration_finished(self, error, _r):
        if error == 0x20000502:
            print "CalibCompute failed because not enough data was collected"
        elif error != 0:
            print "CalibCompute failed because of a server error", error
        else:
            print "Great success!"
        self.eyetracker.StopCalibration(lambda *x, **y: None)
    
    def save_calibration(self):
        calibration = self.eyetracker.GetCalibration()
        calibration_file = open(os.path.expanduser("~/calib.bin"), "wb")
        calibration_file.write(calibration.rawData)
        calibration_file.close()
    
    def close(self):
        self.eyetracker_thread.kill()


if __name__ == "__main__":
    EtrCalibrationTobii(settings.MULTIPLEXER_ADDRESSES).run()
