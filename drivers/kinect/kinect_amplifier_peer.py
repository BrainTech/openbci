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

		self.device_uri = str(self.get_param('device_uri'))
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

		if file_name:
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
		if self.device_uri:
			rc = self.device.open(self.device_uri)  
		else: 
			rc = self.device.open()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Device open failed.")

		if self.device.isImageRegistrationModeSupported(IMAGE_REGISTRATION_DEPTH_TO_COLOR):
			self.device.setImageRegistrationMode(IMAGE_REGISTRATION_DEPTH_TO_COLOR)
		if not self.device.getDepthColorSyncEnabled():
			self.device.setDepthColorSyncEnabled(True)

		self.recorder = Recorder()
		if file_name:
			rc = self.recorder.create(os.path.join(directory, file_name))
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Recorder create failed.")

		self.ready()

	def finish(self):
		cv2.destroyAllWindows()
		self.data_file.close()
		if self.recorder.isValid(): 
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
				try:
					cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1)
				except ValueError:
					return

	def draw_user(self, img, skeleton):
		for j in self.joints:
			joint = skeleton.getJoint(j)
			rc, x_new, y_new = self.ut.convertJointCoordinatesToDepth(joint.position.x, joint.position.y, joint.position.z)
			if joint.positionConfidence > 0.5:
				try:
					cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1)
				except ValueError:
					pass
			else:
				try:
					cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 0, 255), -1)
				except ValueError:
					pass
		for c in self.connections:
			joint_1 = skeleton.getJoint(c[0])
			joint_2 = skeleton.getJoint(c[1])
			rc, x1, y1 = self.ut.convertJointCoordinatesToDepth(joint_1.position.x, joint_1.position.y, joint_1.position.z)
			rc, x2, y2 = self.ut.convertJointCoordinatesToDepth(joint_2.position.x, joint_2.position.y, joint_2.position.z)
			try:
				cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255))
			except ValueError:
				pass

	def serialize_skeleton(self, joints_coordinates, hands_coordinates, header):
		ffm = '??ifiQiQiQiQ' + 2*'ifffff' + 'ifff' + 15*'iffffff'				
		if joints_coordinates is not None and hands_coordinates is not None:
			tracking = [1, 1]
			tracking.extend(header)
			data = []		
			data.extend(tracking + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		elif joints_coordinates is not None:
			tracking = [1, 0]
			tracking.extend(header)
			hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
			data = []		
			data.extend(tracking + hands_coordinates + joints_coordinates)
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		elif hands_coordinates is not None:
			tracking = [0, 1]
			tracking.extend(header)
			joints_coordinates = []
			data = []
			joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
			data.extend(tracking + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)
		else:
			tracking = [0, 0]
			tracking.extend(header)
			hands_coordinates = 2*[0, 0.0, 0.0, 0.0, 0.0, 0.0]
			joints_coordinates = []
			data = []
			joints_coordinates.extend([0, 0.0, 0.0, 0.0] + 15*[0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
			data.extend(tracking + hands_coordinates + joints_coordinates)	
			s = struct.pack(ffm, *data)
			self.data_file.write(s)

	def deserialize_skeleton(self):
		ffm = '??ifiQiQiQiQ' + 2*'ifffff' + 'ifff' + 15*'iffffff'
		frame_size = struct.calcsize(ffm)
		buf = self.data_file.read(frame_size)
		if not buf: return
		data = struct.unpack(ffm, buf)
		return data

	# def draw_from_file(self, frame, img):
	# 	if frame[1] and frame[2]:
	# 		center = (frame[7], frame[8])
	# 		if center[0] and center[1]:
	# 			cv2.circle(img, (int(center[0]), int(center[1])), 8, (0, 255, 0), -1)

	# 		# if frame[9]:

	# 		# 	center2 = (frame[13], frame[14])
	# 		# 	if center2[0] and center2[1]:
	# 		# 		try:
	# 		# 			cv2.circle(img, (int(center2[0]), int(center2[1])), 8, (0, 255, 0), -1)
	# 		# 		except TypeError:
	# 		# 			pass
	# 		if frame[15]:
	# 			head = (frame[21], frame[22])
	# 			cv2.circle(img, (int(head[0]), int(head[1])), 8, (0, 255, 0), -1)

	# 	elif frame[1]:	
	# 		j = frame[17:]
	# 		for i in xrange(14):
	# 			center = (j[(i+1)*7], j[(i+1)*7+1])
	# 			cv2.circle(img, (int(center[0]), int(center[1])), 8, (0, 255, 0), -1)

	# 	elif frame[2]: 
	# 		center = (frame[7], frame[8])

	# 		cv2.circle(img, (int(center[0]), int(center[1])), 8, (0, 255, 0), -1)

	# 		if frame[9]:
	# 			center = (frame[13], frame[14])
	# 			if center[0] and center[1]:
	# 				try:
	# 					cv2.circle(img, (int(center[0]), int(center[1])), 8, (0, 255, 0), -1)
	# 				except ValueError:
	# 					pass

	def get_hands_coordinates(self):
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
		return hands_coordinates

	def get_joints_coordinates(self):
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
		return joints_coordinates

	def get_frames(self):
		frames = []
		if self.color_frame.isValid() and self.depth_frame.isValid():
			frames.extend([self.color_frame.frameIndex, self.color_frame.timestamp, self.depth_frame.frameIndex, self.depth_frame.timestamp])
		elif self.depth_frame.isValid():
			frames.extend([0, 0, 0, self.depth_frame.frameIndex, self.depth_frame.timestamp])
		elif self.color_frame.isValid():
			frames.extend([self.color_frame.frameIndex, self.color_frame.timestamp, 0, 0])
		return frames

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
			f_name = os.path.basename(self.device_uri)
			f_name = os.path.splitext(f_name)[0]
			self.data_file = open(os.path.join(os.path.expanduser('~'), f_name), 'rb')	### try
			self.playback = self.device.getPlaybackControl()
			if self.playback.isValid():
				self.playback.setRepeatEnabled(False)

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
			time_rec_start = time.time()
		
		if self.hand_tracking and not self.device.isFile():
			self.ht = HandTracker()
			rc = self.ht.create(self.device)
			if rc != NITE_STATUS_OK:
				self.logger.error('Creating hand tracker failed.')
			self.ht.startGestureDetection(GESTURE_WAVE)
			self.ht.startGestureDetection(GESTURE_CLICK)
			self.ht.startGestureDetection(GESTURE_HAND_RAISE)

		if self.skeleton_tracking and not self.device.isFile():
			self.ut = UserTracker()
			rc = self.ut.create()
			if rc != NITE_STATUS_OK:
				self.logger.error('Creating user tracker failed.')

		licznik = 0

		while True:
			k = cv2.waitKey(10)

			rc, self.color_frame = self.color.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading color frame.")

			rc, self.depth_frame = self.depth.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading depth frame.")
			
			licznik += 1

			if self.color_frame is not None and self.color_frame.isValid():
				data_rgb = self.color_frame.data
				data_rgb = cv2.cvtColor(data_rgb, cv2.COLOR_BGR2RGB)		
			if self.depth_frame is not None and self.depth_frame.isValid():
				data_depth = self.depth_frame.data
				data_depth = np.float32(data_depth)
				data_depth = data_depth * (-255.0/3200.0) + (800.0*255.0/3200.0)
				data_depth = data_depth.astype('uint8')
				data_depth = cv2.cvtColor(data_depth, cv2.COLOR_GRAY2RGB)

			if self.hand_tracking and not self.device.isFile():
				rc, frame = self.ht.readFrame()
				if rc != NITE_STATUS_OK:
					self.logger.error('Error reading hand tracker frame')
				gestures = frame.gestures
				for g in gestures:
					if g.isComplete():
						rc, newId = self.ht.startHandTracking(g.currentPosition)
				self.hands = frame.hands
				self.time_hands = frame.timestamp
				self.frame_id_hands = frame.frameIndex
				self.draw_hands(data_depth, self.hands)
				self.draw_hands(data_rgb, self.hands)

			if self.skeleton_tracking and not self.device.isFile():
				rc, frame = self.ut.readFrame()
				if rc != OPENNI_STATUS_OK:
					self.logger.error('Error reading user tracker frame')
				self.frame_id_skeleton = frame.frameIndex
				self.time_skeleton = frame.timestamp
				self.users = frame.users
				for u in self.users:
					if u.isNew():
						self.ut.startSkeletonTracking(u.id)
					elif u.skeleton.state == SKELETON_TRACKED:
						self.draw_user(data_rgb, u.skeleton)
						self.draw_user(data_depth, u.skeleton)

			if not self.device.isFile() and self.recorder.isValid():
				if self.hand_tracking and self.skeleton_tracking:
					header = [licznik, time_rec_start, self.frame_id_hands, self.time_hands, self.frame_id_skeleton, self.time_skeleton]
					frames = self.get_frames()
					header.extend(frames)
					hands_coordinates = self.get_hands_coordinates()
					joints_coordinates = self.get_joints_coordinates()
					self.serialize_skeleton(joints_coordinates, hands_coordinates, header)			
				elif self.hand_tracking:
					header = [licznik, time_rec_start, self.frame_id_hands, self.time_hands, 0, 0]
					frames = self.get_frames()
					header.extend(frames)
					hands_coordinates = self.get_hands_coordinates()
					self.serialize_skeleton(None, hands_coordinates, header)
				elif self.skeleton_tracking:
					header = [licznik, time_rec_start, 0, 0, self.frame_id_skeleton, self.time_skeleton]
					frames = self.get_frames()
					header.extend(frames)
					joints_coordinates = self.get_joints_coordinates()
					self.serialize_skeleton(joints_coordinates, None, header)
				else:
					header = [licznik, time_rec_start, 0, 0, 0, 0]
					frames = self.get_frames()
					header.extend(frames)
					self.serialize_skeleton(self.frame_id, None, None, header)

			if self.video_type_rgb:
				if self.device.isFile():
					if self.skeleton_tracking or self.hand_tracking:
						data = self.deserialize_skeleton()
						#if not data: break
						# try:
						# 	self.draw_from_file(data, data_rgb)
						# except ValueError:
						# 	pass
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


