#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
from KinectAmplifier import KinectAmplifier

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import settings, variables_pb2

g_exiting = False

class KinectAmplifierClient(ConfiguredClient):
    def __init__(self, addresses):
        super(KinectAmplifierClient, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

        self.logger.info('KinectAmplifierClient is starting...')
        self.init_signals()

        config = {
            'mode': self.get_param('mode'),
            #for online mode:
            'capture_raw': bool(int(self.get_param('capture_raw'))),
            'out_raw_file_path': str(self.get_param('out_raw_file_path')),
            'capture_hands': bool(int(self.get_param('capture_hands'))),
            'capture_skeleton': bool(int(self.get_param('capture_skeleton'))),
            'out_algs_file_path': str(self.get_param('out_algs_file_path')),
            #for offline mode:
            'in_raw_file_path': str(self.get_param('in_raw_file_path')),
            'in_algs_file_path': str(self.get_param('in_algs_file_path')),
            #for both modes:
            'show_hands': bool(int(self.get_param('show_hands'))),
            'show_skeleton': bool(int(self.get_param('show_skeleton'))),   
            'show_rgb': bool(int(self.get_param('show_rgb'))),
            'show_depth': bool(int(self.get_param('show_depth'))),
        }

        def loop_cb(k):
            if g_exiting:
                return True
            return False
            
        self.kinect = KinectAmplifier(config, loop_cb)
        self.ready()

    def finish(self):
        self.kinect.finish()
        sys.exit(0)

    def run(self):
        self.kinect.run()

    def init_signals(self):
        self.logger.info('Initializing signals in Kinect peer...')
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        if sys.platform == 'win32':
            signal.signal(signal.SIGBREAK, self.signal_handler())

    def signal_handler(self):
        def handler(signum, frame):
            self.logger.warning('Received signal ' + str(signum) + '. Finish kinect module!')
            g_exiting = True
            sys.exit(-signum)
        return handler

if __name__ == '__main__':
    kinect = KinectAmplifierClient(settings.MULTIPLEXER_ADDRESSES)
    kinect.run()
