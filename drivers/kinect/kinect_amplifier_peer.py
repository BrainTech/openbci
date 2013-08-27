#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os.path, signal, threading, struct

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from nite2 import *
import cv2
import numpy as np

g_exiting = False

class JointStruct(struct.Struct):
	def __init__(self):
		super(JointStruct, self).__init__('iffffff')

class HandStruct(struct.Struct):
	def __init__(self):
		super(HandStruct, self).__init__('ifffff')

class UserStruct(struct.Struct):
	def __init__(self):
		super(UserStruct, self).__init__('hfffi')

class FrameStruct(struct.Struct):
	def __init__(self):
		super(FrameStruct, self).__init__('iQ')

class HeaderStruct(struct.Struct):
	def __init__(self):
		super(HeaderStruct, self).__init__('i??fiQiQ')

class Point3Mock(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class JointMock(object):
	def __init__(self, joint_id, positionConfidence, point, x_converted, y_converted):
		self.id = joint_id
		self.positionConfidence = positionConfidence
		self.x = point.x
		self.y = point.y
		self.z = point.z
		self.x_converted = x_converted
		self.y_converted = y_converted

class SkeletonFrameMock(object):
	def __init__(self, frame_id, frame_timestamp, user_id, point, user_state, joints):
		self.frame_id = frame_id
		self.frame_timestamp = frame_timestamp
		self.user_id = user_id
		self.user_x = point.x
		self.user_y = point.y
		self.user_z = point.z
		self.user_state = user_state
		self.joints = joints

class HandDataMock(object):
	def __init__(self, hand_id, point, x_converted, y_converted):
		self.id = hand_id
		self.x = point.x
		self.y = point.y
		self.z = point.z
		self.x_converted = x_converted
		self.y_converted = y_converted

class HandFrameMock(object):
	def __init__(self, frame_id, frame_timestamp, hands):
		self.id = frame_id
		self.frame_timestamp = frame_timestamp
		self.hands = hands

class Serialization:
	def __init__(self):
		self.joint_s = JointStruct()
		self.hand_s = HandStruct()
		self.user_s = UserStruct()
		self.frame_s = FrameStruct()
		self.header_s = HeaderStruct()

	def serialize_frame(self, header, hand_frame, user_frame):
		buf = self.header_s.pack(*header)
		buf += self.serialize_skeleton(user_frame)
		buf += self.serialize_hands(hand_frame)
		return buf

	def unserialize_frame(self, data_file):
		data = []
		try:
			data += self.header_s.unpack(data_file.read(self.header_s.size))
			data.append(self.unserialize_skeleton(data_file))
			data.append(self.unserialize_hands(data_file))
		except struct.error:
			return
		return data

	def register_hand_coordinates(self, convert_hand_coordinates):
		self.convert_hand_coordinates = convert_hand_coordinates

	def register_joint_coordinates(self, convert_joint_coordinates):
		self.convert_joint_coordinates = convert_joint_coordinates

	def serialize_hands(self, hand_frame):
		if hand_frame is not None:
			buf = self.frame_s.pack(hand_frame.frameIndex, 
									hand_frame.timestamp)
			hands = hand_frame.hands
			if hands:
				if len(hands) == 1:
					hand = hands[0]
					if hand.isTracking():
						rc, x_new, y_new = self.convert_hand_coordinates(hand.position.x, hand.position.y, hand.position.z)
						buf += self.hand_s.pack(hand.id,
												hand.position.x, 
												hand.position.y, 
												hand.position.z, 
												x_new, 
												y_new)
					else:
						buf += self.hand_s.pack(0, 0, 0, 0, 0, 0)
					buf += self.hand_s.pack(0, 0, 0, 0, 0, 0)
				else:
					for hand in hands[:2]:
						rc, x_new, y_new = self.convert_hand_coordinates(hand.position.x, hand.position.y, hand.position.z)
						buf += self.hand_s.pack(hand.id, 
												hand.position.x, 
										   		hand.position.y, 
										   		hand.position.z, 
										   		x_new, 
										   		y_new)
			else:
				for i in range(2):
					buf += self.hand_s.pack(0, 0, 0, 0, 0, 0)
		else:
			buf = self.frame_s.pack(0, 0)
			for i in range(2):
				buf += self.hand_s.pack(0, 0, 0, 0, 0, 0)
		return buf

	def serialize_joint(self, joint):
		if joint is not None:
			rc, x_new, y_new = self.convert_joint_coordinates(joint.position.x, joint.position.y, joint.position.z)
			return self.joint_s.pack(joint.type, 
	    						joint.positionConfidence,
	    						joint.position.x,
	    						joint.position.y,
	    						joint.position.z,
	    						x_new,
	    						y_new)
		else:
			return self.joint_s.pack(0, 0, 0, 0, 0, 0, 0)

	def serialize_skeleton(self, user_frame):
		if user_frame is not None:
			buf = self.frame_s.pack(user_frame.frameIndex, 
									user_frame.timestamp)
			users = user_frame.users
			if users:
				user = users[0]
				user_coordinates = user.centerOfMass
				state = int(user.skeleton.state)
				buf += self.user_s.pack(user.id, 
										user_coordinates.x, 
										user_coordinates.y, 
										user_coordinates.z, 
										state)
				for i in xrange(15):
					buf += self.serialize_joint(user.skeleton[JointType(i)])
			else:
				buf += self.user_s.pack(0, 0, 0, 0, 0)
				for i in xrange(15):
					buf += self.serialize_joint(None)
		else:
			buf = self.frame_s.pack(0, 0)
			buf += self.user_s.pack(0, 0, 0, 0, 0)
			for i in xrange(15):
				buf += self.serialize_joint(None)
		return buf

	def unserialize_hands(self, f):
		v = self.frame_s.unpack(f.read(self.frame_s.size))
		data = []
		for i in xrange(2):
			hands = self.hand_s.unpack(f.read(self.hand_s.size))
			data.append(HandDataMock(hands[0], Point3Mock(hands[1], hands[2], hands[3]), hands[4], hands[5]))
		return HandFrameMock(v[0], v[1], data)

	def unserialize_joint(self, f):
		v = self.joint_s.unpack(f.read(self.joint_s.size))
		return JointMock(v[0], v[1], Point3Mock(v[2], v[3], v[4]), v[5], v[6])
	                       
	def unserialize_skeleton(self, f):
		v = []
		v += self.frame_s.unpack(f.read(self.frame_s.size))
		v += self.user_s.unpack(f.read(self.user_s.size))
		joints = []
		for i in xrange(15):
			joints.append(self.unserialize_joint(f))
		return SkeletonFrameMock(v[0], v[1], v[2], Point3Mock(v[3], v[4], v[5]), v[6], joints)

class KinectAmplifier(ConfiguredClient):

	connections = [(JOINT_HEAD, JOINT_NECK),
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
	       		   (JOINT_RIGHT_KNEE, JOINT_RIGHT_FOOT)]

	joints = [JOINT_HEAD,
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
	  		  JOINT_TORSO]

	def __init__(self, addresses):
		super(KinectAmplifier, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

		self.logger.info("Started initializing Kinect...")
		self.init_signals()

		self.device_uri = str(self.get_param('device_uri'))
		self.file_name = str(self.get_param('file_name'))
		self.directory = str(self.get_param('directory'))
		if not self.directory:
			self.directory = os.path.expanduser("~")
		if not os.path.exists(self.directory):
			self.logger.error("Directory doesn't exist.")
			sys.exit(1)

		self.rgb_capture = eval(self.get_param('rgb_capture'))
		self.depth_capture = eval(self.get_param('depth_capture'))
		self.hand_tracking = eval(self.get_param('hand_tracking'))
		self.skeleton_tracking = eval(self.get_param('skeleton_tracking'))
		self.video_type_rgb = eval(self.get_param('video_type_rgb'))
		self.video_type_depth = eval(self.get_param('video_type_depth'))

		if self.file_name:
			f_name = self.file_name.split('.')
			f_name = f_name[0]
			self.data_file = open(os.path.join(self.directory, f_name), 'ab')

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
					cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 180, 247), -1)
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

	def draw_point(self, center, img, color):
		if center[0] and center[1]:
			try:
				cv2.circle(img, (int(center[0]), int(center[1])), 8, color, -1)
			except ValueError:
				return

	def draw_from_file(self, frame, img):
		if frame[1] or frame[2]:
			user_data = frame[8]
			hand_data = frame[9]
			h = hand_data.hands
			if h[0].id:
				center = (h[0].x_converted, h[0].y_converted)
				self.draw_point(center, img, (0, 180, 247))
			if h[1].id:
				center = (h[1].x_converted, h[1].y_converted)
				self.draw_point(center, img, (0, 180, 247))
			if user_data.user_id and SkeletonState(user_data.user_state) == SKELETON_TRACKED:
				for i in xrange(15):
					joint = user_data.joints[i]
					center = (joint.x_converted, joint.y_converted)
					if joint.positionConfidence > 0.5:
						self.draw_point(center, img, (0, 255, 0))
					else:
						self.draw_point(center, img, (0, 0, 255))

	def get_frames(self):
		frames = []
		if self.color_frame.isValid() and self.depth_frame.isValid():
			frames.extend([self.color_frame.frameIndex, self.color_frame.timestamp, self.depth_frame.frameIndex, self.depth_frame.timestamp])
		elif self.depth_frame.isValid():
			frames.extend([0, 0, self.depth_frame.frameIndex, self.depth_frame.timestamp])
		elif self.color_frame.isValid():
			frames.extend([self.color_frame.frameIndex, self.color_frame.timestamp, 0, 0])
		return frames

	def run(self):
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

		self.color = VideoStream()
		self.depth = VideoStream()

		rc = self.color.create(self.device, SENSOR_COLOR)
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Color stream create failed.")
		rc = self.depth.create(self.device, SENSOR_DEPTH)
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Depth stream create failed.")

		self.recorder = Recorder()
		if self.file_name:
			rc = self.recorder.create(os.path.join(self.directory, self.file_name))
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Recorder create failed.")

		if self.recorder.isValid() and not self.device.isFile():
			if self.rgb_capture:
				rc = self.recorder.attach(self.color, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach color error.")
			if self.depth_capture:
				rc = self.recorder.attach(self.depth, True)
				if rc != OPENNI_STATUS_OK:
					self.logger.error("Recorder attach depth error.")
			rc = self.recorder.start()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Recorder start error.")
			self.time_rec_start = time.time()

		if self.device.isFile():
			f_name = os.path.basename(self.device_uri)
			f_name = os.path.splitext(f_name)[0]
			self.data_file = open(os.path.join(os.path.expanduser('~'), f_name), 'rb')
			self.playback = self.device.getPlaybackControl()
			if self.playback.isValid():
				self.playback.setRepeatEnabled(False)

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

		self.ready()

		s = Serialization()
		s.register_hand_coordinates(lambda x, y, z: self.ht.convertHandCoordinatesToDepth(x, y, z))
		s.register_joint_coordinates(lambda x, y, z: self.ut.convertJointCoordinatesToDepth(x, y, z))

		rc = self.depth.start()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Depth stream start failed.")
			self.depth.destroy()
		rc = self.color.start()
		if rc != OPENNI_STATUS_OK:
			self.logger.error("Color stream start failed.")
			self.color.destroy()

		frame_index = 0
		current_frame_rgb = None
		# current_frame_depth = None

		while True:
			k = cv2.waitKey(10)

			if g_exiting:
				break

			rc, self.color_frame = self.color.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading color frame.")

			rc, self.depth_frame = self.depth.readFrame()
			if rc != OPENNI_STATUS_OK:
				self.logger.error("Error reading depth frame.")

			frame_index += 1

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
				rc, self.hand_frame = self.ht.readFrame()
				if rc != NITE_STATUS_OK:
					self.logger.error('Error reading hand tracker frame')
				gestures = self.hand_frame.gestures
				for g in gestures:
					if g.isComplete():
						rc, newId = self.ht.startHandTracking(g.currentPosition)
				self.hands = self.hand_frame.hands
				self.draw_hands(data_depth, self.hands)
				self.draw_hands(data_rgb, self.hands)

			if self.skeleton_tracking and not self.device.isFile():
				rc, self.user_frame = self.ut.readFrame()
				if rc != OPENNI_STATUS_OK:
					self.logger.error('Error reading user tracker frame')
				self.users = self.user_frame.users
				for u in self.users:
					if u.isNew():
						self.ut.startSkeletonTracking(u.id)
					elif u.skeleton.state == SKELETON_TRACKED:
						self.draw_user(data_rgb, u.skeleton)
						self.draw_user(data_depth, u.skeleton)

			if not self.device.isFile() and self.recorder.isValid():
				if self.hand_tracking and self.skeleton_tracking:
					header = [frame_index, 1, 1, self.time_rec_start]
					header += self.get_frames()
					self.data_file.write(s.serialize_frame(header, self.hand_frame, self.user_frame))
				elif self.hand_tracking:
					header = [frame_index, 0, 1, self.time_rec_start]
					header += self.get_frames()
					self.data_file.write(s.serialize_frame(header, self.hand_frame, None))
				elif self.skeleton_tracking:
					header = [frame_index, 1, 0, self.time_rec_start]
					header += self.get_frames()
					self.data_file.write(s.serialize_frame(header, None, self.user_frame))
				else:
					header = [frame_index, 0, 0, self.time_rec_start]
					header += self.get_frames()
					self.data_file.write(s.serialize_frame(header, None, None))

			if self.video_type_rgb:
				if self.device.isFile():
					if self.skeleton_tracking or self.hand_tracking:
						if current_frame_rgb is None:
							data = s.unserialize_frame(self.data_file)
							if not data: break
							current_frame_rgb = data[4]
							self.draw_from_file(data, data_rgb)
							cv2.imshow('color', data_rgb)
							data = s.unserialize_frame(self.data_file)
							if not data: break
						elif data[4] != current_frame_rgb + 1:
							current_frame_rgb += 1
						elif data[4] == current_frame_rgb + 1:
							self.draw_from_file(data, data_rgb)
							cv2.imshow('color', data_rgb)
							current_frame_rgb = data[4]
							data = s.unserialize_frame(self.data_file)	
							if not data: break
				else:
					cv2.imshow('color', data_rgb)
			if self.video_type_depth:
				cv2.imshow('depth', data_depth)

		self.finish()

	def init_signals(self):
		self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
		signal.signal(signal.SIGTERM, self.signal_handler())
		signal.signal(signal.SIGINT, self.signal_handler())
		if sys.platform == 'win32':
			signal.signal(signal.SIGBREAK, self.signal_handler())
        
	def signal_handler(self):
		def handler(signum, frame):
			self.logger.warning("Got signal " + str(signum) + "!!! Sending diodes ON!")
			g_exiting = True
			sys.exit(-signum)
		return handler

if __name__ == "__main__":
    KinectAmplifier(settings.MULTIPLEXER_ADDRESSES).run()


