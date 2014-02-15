#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os.path, signal, threading, struct

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

import cv2
import numpy as np
from obci.configs import settings, variables_pb2
from KinectAmplifier import JointStruct, HandStruct, UserStruct, FrameStruct, HeaderStruct, Point3Mock, JointMock, SkeletonFrameMock, HandDataMock, HandFrameMock, Serialization, KinectAmplifier

from nite2 import *

g_exiting = False

class KinectAmplifierClient(ConfiguredClient):
    def __init__(self, addresses):
        super(KinectAmplifierClient, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

        self.logger.info('KinectAmplifierClient is starting...')
        self.init_signals()

        config = {}
        config['device_uri'] = str(self.get_param('device_uri'))
        config['file_name']  = str(self.get_param('file_name'))
        config['directory']  = str(self.get_param('directory'))

        config['rgb_capture']       = bool(eval(self.get_param('rgb_capture')))
        config['depth_capture']     = bool(eval(self.get_param('depth_capture')))
        config['hand_tracking']     = bool(eval(self.get_param('hand_tracking')))
        config['skeleton_tracking'] = bool(eval(self.get_param('skeleton_tracking')))
        config['video_type_rgb']    = bool(eval(self.get_param('video_type_rgb')))
        config['video_type_depth']  = bool(eval(self.get_param('video_type_depth')))

        def ready_cb():
            self.ready()
        def loop_cb(k):
            if g_exiting:
                return True
            return False
        self.kinect = KinectAmplifier(config, ready_cb, loop_cb)

    def finish(self):
        self.kinect.finish()
        sys.exit(0)

    def run(self):
        self.kinect.run()

    def init_signals(self):
        self.logger.info('Initializing signals in appliance cleaner')
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler())

    def signal_handler(self):
        def handler(signum, frame):
            self.logger.warning('Received signal ' + str(signum) + '. Sending diodes ON!')
            g_exiting = True
            sys.exit(-signum)
        return handler

if __name__ == '__main__':
    kinect = KinectAmplifierClient(settings.MULTIPLEXER_ADDRESSES)
    kinect.run()
