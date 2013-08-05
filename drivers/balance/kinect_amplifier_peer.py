#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os.path, signal, threading

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
import pykinect
from pykinect import VideoType

class KinectAmplifier(ConfiguredClient):
	def __init__(self, addresses):
		super(KinectAmplifier, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

		self.logger.info("Started initializing Kinect...")
		self.init_signals()

		self.k = pykinect.Kinect()

		device_uri = str(self.get_param('device_uri'))
		file_name = str(self.get_param('file_name'))
		directory = str(self.get_param('directory'))

		if not os.path.exists(directory):
			self.logger.error("Directory doesn't exist.")
			sys.exit(1)

		rgb_capture = eval(self.get_param('rgb_capture'))
		depth_capture = eval(self.get_param('depth_capture'))
		hand_tracking = eval(self.get_param('hand_tracking'))
		skeleton_tracking = eval(self.get_param('skeleton_tracking'))

		self.video_type_rgb = eval(self.get_param('video_type_rgb'))
		self.video_type_depth = eval(self.get_param('video_type_depth'))
		self.kinect_error = False
		self.kinect_lock = threading.RLock()
		config = {'rgb_capture': rgb_capture,
    			  'depth_capture': depth_capture,
   				  'hand_tracking': hand_tracking,
  				  'skeleton_tracking': skeleton_tracking,
  				  'device_uri': device_uri}

		self.k.register_callback(self.error_callback)
		try:
			self.k.init(os.path.join(directory,file_name), config)
		except:
			self.logger.error("Initialization failed.")
			sys.exit(1)
		self.ready()

	def run(self):
		while True:
			with self.kinect_lock:
				if self.kinect_error:
					self.k.finish()
					sys.exit(1)
			if self.video_type_rgb and self.video_type_depth:
				self.k.show_video(VideoType.RgbAndDepth)
			elif self.video_type_rgb:
				self.k.show_video(VideoType.Rgb)
			elif self.video_type_depth:
				self.k.show_video(VideoType.Depth)
			
	def error_callback(self, msg):
		self.logger.error(msg)
		with self.kinect_lock:
			self.kinect_error = True

	def init_signals(self):
		self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
		signal.signal(signal.SIGTERM, self.signal_handler())
		signal.signal(signal.SIGINT, self.signal_handler())
        
	def signal_handler(self):
		def handler(signum, frame):
			self.logger.warning("Got aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaasignal " + str(signum) + "!!! Sending diodes ON!")
			self.k.finish()
			sys.exit(-signum)
		return handler

if __name__ == "__main__":
    KinectAmplifier(settings.MULTIPLEXER_ADDRESSES).run()


