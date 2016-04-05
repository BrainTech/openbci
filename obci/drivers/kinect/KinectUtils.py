#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from nite2 import *

class KinectException(Exception):
    pass

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
        super(HeaderStruct, self).__init__('i??diQiQ')

class Point3Mock(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class JointMock(object):
    def __init__(self, id, positionConfidence, x, y, z, x_converted, y_converted):
        self.id = id
        self.positionConfidence = positionConfidence
        self.x = x
        self.y = y
        self.z = z
        self.x_converted = x_converted
        self.y_converted = y_converted

class SkeletonFrameMock(object):
    def __init__(self, frame_index, frame_timestamp, user_id, x, y, z, user_state, joints):
        self.frame_index = frame_index
        self.frame_timestamp = frame_timestamp
        self.user_id = user_id
        self.user_x = x
        self.user_y = y
        self.user_z = z
        self.user_state = user_state
        self.joints = joints

class HandDataMock(object):
    def __init__(self, hand_id, x, y, z, x_converted, y_converted):
        self.id = hand_id
        self.x = x
        self.y = y
        self.z = z
        self.x_converted = x_converted
        self.y_converted = y_converted

class HandFrameMock(object):
    def __init__(self, frame_index, frame_timestamp, hands):
        self.frame_index = frame_index
        self.frame_timestamp = frame_timestamp
        self.hands = hands

class Serialization(object):
    def __init__(self):
        self.joint_s = JointStruct()
        self.hand_s = HandStruct()
        self.user_s = UserStruct()
        self.frame_s = FrameStruct()
        self.header_s = HeaderStruct()

    def serialize_frame(self, header, hand_frame, user_frame, frame_index):
        buf = self.header_s.pack(*header)
        buf += self.serialize_skeleton(user_frame, frame_index)
        buf += self.serialize_hands(hand_frame, frame_index)
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

    def serialize_hands(self, hand_frame, frame_index):
        if hand_frame is not None:
            buf = self.frame_s.pack(frame_index, hand_frame.timestamp)
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
            pos = joint.position
            rc, x_new, y_new = self.convert_joint_coordinates(pos.x, pos.y, pos.z)
            return self.joint_s.pack(joint.type,
                                     joint.positionConfidence,
                                     joint.position.x,
                                     joint.position.y,
                                     joint.position.z,
                                     x_new,
                                     y_new)
        else:
            return self.joint_s.pack(0, 0, 0, 0, 0, 0, 0)

    def serialize_skeleton(self, user_frame, frame_index):
        if user_frame is not None:
            buf = self.frame_s.pack(frame_index, user_frame.timestamp)
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
            data.append(HandDataMock(hands[0], hands[1], hands[2], hands[3], hands[4], hands[5]))
        return HandFrameMock(v[0], v[1], data)

    def unserialize_joint(self, f):
        v = self.joint_s.unpack(f.read(self.joint_s.size))
        return JointMock(*v)

    def unserialize_skeleton(self, f):
        v = []
        v += self.frame_s.unpack(f.read(self.frame_s.size))
        v += self.user_s.unpack(f.read(self.user_s.size))
        joints = []
        for i in xrange(15):
            joints.append(self.unserialize_joint(f))
        return SkeletonFrameMock(v[0], v[1], v[2], v[3], v[4], v[5], v[6], joints)
        
