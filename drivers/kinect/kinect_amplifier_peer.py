#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os.path, signal, threading, struct

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

		f_name = file_name.split('.')
		f_name = f_name[0]
		self.data_file = open(os.path.join(directory, f_name), 'wb')
		
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
		self.data_file.close()
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

	def serialize_skeleton(self, frame_id, joints_coordinates, hands_coordinates):
		ffm = 'i??' + 2*'ifffff' + 'ifff' + 15*'iffffff'				
		if joints_coordinates is not None and hands_coordinates is not None:
			header = [frame_id, 1, 1]
			data = []		
			data.extend(header + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		elif joints_coordinates is not None:
			header = [frame_id, 1, 0]
			hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
			data = []		
			data.extend(header + hands_coordinates + joints_coordinates)
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		elif hands_coordinates is not None:
			header = [frame_id, 0, 1]
			joints_coordinates = []
			data = []
			joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
			data.extend(header + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		else:
			header = [frame_id, 0, 0]
			hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
			joints_coordinates = []
			data = []
			joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
			data.extend(header + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)

	def deserialize_skeleton(self, filename):
		ffm = 'i??' + 2*'ifffff' + 'ifff' + 15*'iffffff'
		f = open(filename, 'rb')
		frame_size = struct.calcsize(ffm)
		totalBytes = os.path.getsize(filename)	
		buf = f.read(frame_size)
		if not buf: return
		data = struct.unpack(ffm, buf)
		return data

	def draw_from_file(self, filename, data_rgb):
		frame = deserialize_skeleton(filename)
		#x_new, y_new = 
		
		#cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1) /////TODO

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

			if color_frame.isValid():
				self.frame_id = color_frame.frameIndex
			elif depth_frame.isValid():
				self.frame_id = depth_frame.frameIndex

			print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2', self.frame_id

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
				self.hands = frame.hands
				self.frame_id_hands = frame.frameIndex
				self.draw_hands(data_depth, self.hands)
				self.draw_hands(data_rgb, self.hands)

			if self.skeleton_tracking:
				rc, frame = self.ut.readFrame()
				if rc != OPENNI_STATUS_OK:
					self.logger.error('Error reading user tracker frame')
				self.frame_id_skeleton = frame.frameIndex
				self.users = frame.users
				for u in self.users:
					if u.isNew():
						self.ut.startSkeletonTracking(u.id)
					elif u.skeleton.state == SKELETON_TRACKED:
						self.draw_user(data_rgb, u.skeleton)
						self.draw_user(data_depth, u.skeleton)

			if self.hand_tracking and self.skeleton_tracking:
				hands_coordinates = []
				joints_coordinates = []

				if len(self.hands) == 0:
					hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
				elif len(self.hands) == 1:
					hand = self.hands[0]
					if hand.isTracking():
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(hand.position.x, hand.position.y, hand.position.z)
						hands_coordinates.extend([hand.id, hand.position.x, hand.position.y, hand.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					else:
						hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
				else:
					if self.hands[0].isTracking() and self.hands[1].isTracking():
						for h in self.hands[:2]:
							rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
							hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new])
					elif self.hands[0].isTracking():
						h = self.hands[0]
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
						hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					elif self.hands[1].isTracking():
						h = self.hands[1]
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
						hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					else:
						hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]

				if len(self.users) == 0:
					joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
				else:
					u = self.users[0]
					if u.skeleton.state == SKELETON_TRACKED:
						x, y, z = u.centerOfMass
						joints_coordinates.extend([u.id, x, y, z])
						for i,j in enumerate(self.joints):
							joint = u.skeleton.getJoint(j)
							rc, x_new, y_new = self.ut.convertJointCoordinatesToDepth(joint.position.x, joint.position.y, joint.position.z)
							joints_coordinates.extend([i, joint.positionConfidence, joint.position.x, joint.position.y, joint.position.z, x_new, y_new])	
					else:
						joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

				self.serialize_skeleton(self.frame_id, joints_coordinates, hands_coordinates)
			
			elif self.hand_tracking:
				hands_coordinates = []
				if len(self.hands) == 0:
					hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
				elif len(self.hands) == 1:
					hand = self.hands[0]
					if hand.isTracking():
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(hand.position.x, hand.position.y, hand.position.z)
						hands_coordinates.extend([hand.id, hand.position.x, hand.position.y, hand.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					else:
						hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
				else:
					if self.hands[0].isTracking() and self.hands[1].isTracking():
						for h in self.hands[:2]:
							rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
							hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new])
					elif self.hands[0].isTracking():
						h = self.hands[0]
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
						hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					elif self.hands[1].isTracking():
						h = self.hands[1]
						rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(h.position.x, h.position.y, h.position.z)
						hands_coordinates.extend([h.id, h.position.x, h.position.y, h.position.z, x_new, y_new, 0, 0.0, 0.0, 0.0, 0.0, 0.0])
					else:
						hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
				self.serialize_skeleton(self.frame_id, None, hands_coordinates)

			elif self.skeleton_tracking:
				joints_coordinates = []
				if len(self.users) == 0:
					joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
				else:
					u = self.users[0]
					if u.skeleton.state == SKELETON_TRACKED:
						x, y, z = u.centerOfMass
						joints_coordinates.extend([u.id, x, y, z])
						for i,j in enumerate(self.joints):
							joint = u.skeleton.getJoint(j)
							rc, x_new, y_new = self.ut.convertJointCoordinatesToDepth(joint.position.x, joint.position.y, joint.position.z)
							joints_coordinates.extend([i, joint.positionConfidence, joint.position.x, joint.position.y, joint.position.z, x_new, y_new])	
					else:
						joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
				self.serialize_skeleton(self.frame_id, joints_coordinates, None)

			else:
				self.serialize_skeleton(self.frame_id, None, None)

			if self.video_type_rgb:
				if self.device.isFile():
					if self.skeleton_tracking or self.hand_tracking:
						self.draw_from_file(filename, data_rgb)
						cv2.imshow('color', data_rgb)
					cv2.imshow('color', data_rgb)
				else:
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


