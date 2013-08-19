#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os.path, signal, threading

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from nite2 import *
import cv2
import numpy as np

class KinectAmplifier(ConfiguredClient):
	def __init__(self, addresses):
		super(KinectAmplifier, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

		self.logger.info("Started initializing Kinect...")
		self.init_signals()

		device_uri = str(self.get_param('device_uri'))
		file_name = str(self.get_param('file_name'))
		directory = str(self.get_param('directory'))
		if not directory:
			directory = os.path.expanduser("~")
		if not os.path.exists(directory):
			self.logger.error("Directory doesn't exist.")
			sys.exit(1)

		self.rgb_capture = eval(self.get_param('rgb_capture'))
		self.depth_capture = eval(self.get_param('depth_capture'))
		self.hand_tracking = eval(self.get_param('hand_tracking'))
		self.skeleton_tracking = eval(self.get_param('skeleton_tracking'))
		self.video_type_rgb = eval(self.get_param('video_type_rgb'))
		self.video_type_depth = eval(self.get_param('video_type_depth'))

		self.connections = ((JOINT_HEAD, JOINT_NECK),
	       (JOINT_NECK, JOINT_TORSO),
	       (JOINT_TORSO, JOINT_LEFT_SHOULDER),
	       (JOINT_TORSO, JOINT_RIGHT_SHOULDER),
	       (JOINT_LEFT_SHOULDER, JOINT_LEFT_ELBOW),
	       (JOINT_RIGHT_SHOULDER, JOINT_RIGHT_ELBOW),
	       (JOINT_LEFT_ELBOW, JOINT_LEFT_HAND),
	       (JOINT_RIGHT_ELBOW, JOINT_RIGHT_HAND),
	       (JOINT_TORSO, JOINT_LEFT_HIP),
	       (JOINT_TORSO, JOINT_RIGHT_HIP),
	       (JOINT_LEFT_HIP, JOINT_LEFT_KNEE),
	       (JOINT_RIGHT_HIP, JOINT_RIGHT_KNEE),
	       (JOINT_LEFT_KNEE, JOINT_LEFT_FOOT),
	       (JOINT_RIGHT_KNEE, JOINT_RIGHT_FOOT))

		self.joints = (JOINT_HEAD,
	  		JOINT_LEFT_ELBOW,
			JOINT_LEFT_FOOT,
	 		JOINT_LEFT_HAND,
	  		JOINT_LEFT_HIP,
	  		JOINT_LEFT_KNEE,
	  		JOINT_LEFT_SHOULDER,
	  		JOINT_NECK,
	  		JOINT_RIGHT_ELBOW,
	  		JOINT_RIGHT_FOOT,
	  		JOINT_RIGHT_HAND,
	  		JOINT_RIGHT_HIP,
	  		JOINT_RIGHT_KNEE,
	  		JOINT_RIGHT_SHOULDER,
	  		JOINT_TORSO)
		
		rc = OpenNI.initialize()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("OpenNI initialization failed.")

		rc = NiTE.initialize()
		if rc != NITE_STATUS_OK:
			self.logger.error("NiTE2 initialization failed.")

		self.device = Device()
		if device_uri:
			rc = self.device.open(device_uri)  
		else: 
			rc = self.device.open()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Device open failed.")

		if self.device.isImageRegistrationModeSupported(IMAGE_REGISTRATION_DEPTH_TO_COLOR):
			self.device.setImageRegistrationMode(IMAGE_REGISTRATION_DEPTH_TO_COLOR)

		self.recorder = Recorder()
		if file_name:
			rc = self.recorder.create(os.path.join(directory, file_name))
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Recorder create failed.")

		self.ready()

	def finish(self):
		cv2.destroyAllWindows()
		self.recorder.stop()
		self.recorder.destroy()
		self.color.destroy()
		self.depth.destroy()
		self.device.close()
		NiTE.shutdown()
		OpenNI.shutdown()

	def draw_hands(self, img, hands):
		for h in hands:
			if h.isTracking():
				rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
				cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1)

	def draw_user(self, img, skeleton):
		for j in self.joints:
			joint = skeleton.getJoint(j)
			rc, x_new, y_new = self.ut.convertJointCoordinatesToDepth(joint.position.x, joint.position.y, joint.position.z)
			if joint.positionConfidence > 0.5:
				cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1)
			else:
				cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 0, 255), -1)
		for c in self.connections:
			joint_1 = skeleton.getJoint(c[0])
			joint_2 = skeleton.getJoint(c[1])
			rc, x1, y1 = self.ut.convertJointCoordinatesToDepth(joint_1.position.x, joint_1.position.y, joint_1.position.z)
			rc, x2, y2 = self.ut.convertJointCoordinatesToDepth(joint_2.position.x, joint_2.position.y, joint_2.position.z)
			cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255))

	def run(self):

		self.color = VideoStream()
		self.depth = VideoStream()

		rc = self.color.create(self.device, SENSOR_COLOR)
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Color stream create failed.")
		rc = self.color.start()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Color stream start failed.")
			self.color.destroy()

		rc = self.depth.create(self.device, SENSOR_DEPTH)
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Depth stream create failed.")
		rc = self.depth.start()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Depth stream start failed.")
			self.depth.destroy()

		if self.device.isFile():
			playback = self.device.getPlaybackControl()
			if playback.isValid():
				playback.setRepeatEnabled(False)

		if self.recorder.isValid() and not self.device.isFile():
			if self.rgb_capture and self.depth_capture:
				rc = self.recorder.attach(self.color, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach color error.")
				rc = self.recorder.attach(self.depth, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach depth error.")
			elif self.rgb_capture:
				rc = self.recorder.attach(self.color, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach color error.")
			elif self.depth_capture:
				rc = self.recorder.attach(self.depth, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach depth error.")
			rc = self.recorder.start()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Recorder start error.")
		
		if self.hand_tracking:
			self.ht = HandTracker()
			rc = self.ht.create(self.device)
			if rc != NITE_STATUS_OK:
				self.logger.error('Creating hand tracker failed.')
			self.ht.startGestureDetection(GESTURE_WAVE)
			self.ht.startGestureDetection(GESTURE_CLICK)
			self.ht.startGestureDetection(GESTURE_HAND_RAISE)

		if self.skeleton_tracking:
			self.ut = UserTracker()
			rc = self.ut.create()
			if rc != NITE_STATUS_OK:
				self.logger.error('Creating user tracker failed.')

		while True:
			k = cv2.waitKey(10)

			rc, color_frame = self.color.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading color frame.")

			rc, depth_frame = self.depth.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading depth frame.")

			if color_frame is not None and color_frame.isValid():
				data_rgb = color_frame.data
				data_rgb = cv2.cvtColor(data_rgb, cv2.COLOR_BGR2RGB)
				
			if depth_frame is not None and depth_frame.isValid():
				data_depth = depth_frame.data
				data_depth = np.float32(data_depth)
				data_depth = data_depth * (-255.0/3200.0) + (800.0*255.0/3200.0)
				data_depth = data_depth.astype('uint8')
				data_depth = cv2.cvtColor(data_depth, cv2.COLOR_GRAY2RGB)

			if self.hand_tracking:
				rc, frame = self.ht.readFrame()
				if rc != NITE_STATUS_OK:
					self.logger.error('Error reading hand tracker frame')
				gestures = frame.gestures
				for g in gestures:
					if g.isComplete():
						rc, newId = self.ht.startHandTracking(g.currentPosition)
				hands = frame.hands
				self.draw_hands(data_depth, hands)
				self.draw_hands(data_rgb, hands)

			if self.skeleton_tracking:
				rc, frame = self.ut.readFrame()
				if rc != OPENNI_STATUS_OK:
					self.logger.error('Error reading user tracker frame')
				users = frame.users
				for u in users:
					if u.isNew():
						self.ut.startSkeletonTracking(u.id)
					elif u.skeleton.state == SKELETON_TRACKED:
						self.draw_user(data_rgb, u.skeleton)
						self.draw_user(data_depth, u.skeleton)

			if self.video_type_rgb:
				cv2.imshow('color', data_rgb)
			if self.video_type_depth:
				cv2.imshow('depth', data_depth)

	def init_signals(self):
		self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
		signal.signal(signal.SIGTERM, self.signal_handler())
		signal.signal(signal.SIGINT, self.signal_handler())
		if sys.platform == 'win32':
			signal.signal(signal.SIGBREAK, self.signal_handler())
        
	def signal_handler(self):
		def handler(signum, frame):
			self.logger.warning("Got signal " + str(signum) + "!!! Sending diodes ON!")
			self.finish()
			sys.exit(-signum)
		return handler

if __name__ == "__main__":
    KinectAmplifier(settings.MULTIPLEXER_ADDRESSES).run()


