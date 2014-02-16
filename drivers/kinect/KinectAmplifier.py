#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import sys, time, struct
from nite2 import *

from KinectUtils import *

class KinectAmplifier(object):

    connections = [(JOINT_HEAD,           JOINT_NECK),
                   (JOINT_NECK,           JOINT_TORSO),
                   (JOINT_TORSO,          JOINT_LEFT_SHOULDER),
                   (JOINT_TORSO,          JOINT_RIGHT_SHOULDER),
                   (JOINT_LEFT_SHOULDER,  JOINT_LEFT_ELBOW),
                   (JOINT_RIGHT_SHOULDER, JOINT_RIGHT_ELBOW),
                   (JOINT_LEFT_ELBOW,     JOINT_LEFT_HAND),
                   (JOINT_RIGHT_ELBOW,    JOINT_RIGHT_HAND),
                   (JOINT_TORSO,          JOINT_LEFT_HIP),
                   (JOINT_TORSO,          JOINT_RIGHT_HIP),
                   (JOINT_LEFT_HIP,       JOINT_LEFT_KNEE),
                   (JOINT_RIGHT_HIP,      JOINT_RIGHT_KNEE),
                   (JOINT_LEFT_KNEE,      JOINT_LEFT_FOOT),
                   (JOINT_RIGHT_KNEE,     JOINT_RIGHT_FOOT)]

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

    def __init__(self, config={}, ready_cb=None, loop_cb=None):
        super(KinectAmplifier, self).__init__()

        self.ready_cb = ready_cb
        self.loop_cb = loop_cb

        def default_loop_cb(k):
            if k == 27:
                self.finish()
                return True
            return False
        if self.loop_cb is None:
            self.loop_cb = default_loop_cb

        def _get(name, default):
            return config[name] if name in config else default

        self.mode = _get('mode', 'online')

        if self.mode == 'online':
            #raw capture variables
            self.capture_raw = _get('capture_raw', True)
            self.out_raw_file_path = _get('out_raw_file_path', 'test.oni')
            self.out_raw_file = None

            # algs capture variables
            self.capture_hands = _get('capture_hands', True)
            self.capture_skeleton = _get('capture_skeleton', True)
            self.out_algs_file_path = _get('out_algs_file_path', 'test.algs')
            self.out_algs_file = None

            # reset 'offline' variables
            self.in_raw_file_path = None
            self.in_algs_file_path = None
            self.in_algs_file = None

        elif self.mode == 'offline':
            # input files variables
            self.in_raw_file_path = _get('in_raw_file_path', 'test.oni')
            self.in_algs_file_path = _get('in_algs_file_path', 'test.algs')
            self.in_algs_file = None
            self.capture_raw = False
 
            #reset 'online' variables
            self.out_raw_file_path = None
            self.out_raw_file = None
            self.capture_hands = None
            self.capture_skeleton = None
            self.out_algs_file_path = None
            self.out_algs_file = None
        else:
            raise KinectException("Unrecognised MODE!!!")

        # both modes
        self.show_hands    = _get('show_hands', True)
        self.show_skeleton = _get('show_skeleton', True)     
        self.show_rgb      = _get('show_rgb', True)
        self.show_depth    = _get('show_depth', True)

        self.track_hands    = (self.mode == 'online') and (self.show_hands or self.capture_hands)
        self.track_skeleton = (self.mode == 'online') and (self.show_skeleton or self.show_hands)
        self.capture_algs   = (self.mode == 'online') and (self.capture_hands or self.capture_skeleton)

        self.validate_params()
    
    def validate_params(self):
        if self.capture_algs and not self.capture_raw:
            raise Exception("Cannot capture algs without capturing raw signal!!!")


    def finish(self):
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        if self.in_algs_file:
            self.in_algs_file.close()
        if self.out_algs_file:
            self.out_algs_file.close()
        if self.recorder.isValid():
            self.recorder.stop()
            self.recorder.destroy()
        self.color.destroy()
        self.depth.destroy()
        self.device.close()
        NiTE.shutdown()
        OpenNI.shutdown()

    def draw_hands(self, img, hands):
        if img is None:
            return
        for h in hands:
            if h.isTracking():
                pos = h.position
                rc, x_new, y_new = self.ht.convertHandCoordinatesToDepth(pos.x, pos.y, pos.z)
                try:
                    cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 180, 247), -1)
                except ValueError, OverflowError:
                    return

    def draw_user(self, img, skeleton):
        if img is None:
            return
        for j in self.joints:
            joint = skeleton.getJoint(j)
            pos = joint.position
            rc, x_new, y_new = self.ut.convertJointCoordinatesToDepth(pos.x, pos.y, pos.z)
            if joint.positionConfidence > 0.5:
                try:
                    cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 255, 0), -1)
                except ValueError, OverflowError:
                    pass
            else:
                try:
                    cv2.circle(img, (int(x_new), int(y_new)), 8, (0, 0, 255), -1)
                except ValueError, OverflowError:
                    pass
        for c in self.connections:
            j1 = skeleton.getJoint(c[0]).position
            j2 = skeleton.getJoint(c[1]).position
            rc, x1, y1 = self.ut.convertJointCoordinatesToDepth(j1.x, j1.y, j1.z)
            rc, x2, y2 = self.ut.convertJointCoordinatesToDepth(j2.x, j2.y, j2.z)
            try:
                cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255))
            except ValueError, OverflowError:
                pass

    def _draw_point(self, center, img, color):
        if center[0] and center[1]:
            try:
                cv2.circle(img, (int(center[0]), int(center[1])), 8, color, -1)
            except ValueError, OverflowError:
                pass

    def draw_from_file(self, frame, img):
        if img is None or frame is None:
            return
        if frame[1] or frame[2]:
            user_data = frame[8]
            hand_data = frame[9]
            h = hand_data.hands
            if h[0].id:
                center = (h[0].x_converted, h[0].y_converted)
                self._draw_point(center, img, (0, 180, 247))
            if h[1].id:
                center = (h[1].x_converted, h[1].y_converted)
                self._draw_point(center, img, (0, 180, 247))
            if user_data.user_id and SkeletonState(user_data.user_state) == SKELETON_TRACKED:
                for i in xrange(15):
                    joint = user_data.joints[i]
                    center = (joint.x_converted, joint.y_converted)
                    if joint.positionConfidence > 0.5:
                        self._draw_point(center, img, (0, 255, 0))
                    else:
                        self._draw_point(center, img, (0, 0, 255))

    def get_frames(self):
        color = [self.color_frame.frameIndex, self.color_frame.timestamp] if self.color_frame.isValid() else [0, 0]
        depth = [self.depth_frame.frameIndex, self.depth_frame.timestamp] if self.depth_frame.isValid() else [0, 0]
        return color + depth

    def run(self):
        rc = OpenNI.initialize()
        if rc != OPENNI_STATUS_OK:
            raise KinectException('OpenNI initialization failed.')

        rc = NiTE.initialize()
        if rc != NITE_STATUS_OK:
            raise KinectException('NiTE2 initialization failed.')

        # create device - file or kinect sensor
        self.device = Device()
        if self.mode == 'offline':
            rc = self.device.open(self.in_raw_file_path)
            self.in_algs_file = open(self.in_algs_file_path, 'rb')
        elif self.mode == 'online':
            rc = self.device.open()

        if rc != OPENNI_STATUS_OK:
            raise KinectException('Device open failed: ' + str(OpenNI.getExtendedError()).strip())

        if self.device.isImageRegistrationModeSupported(IMAGE_REGISTRATION_DEPTH_TO_COLOR):
            self.device.setImageRegistrationMode(IMAGE_REGISTRATION_DEPTH_TO_COLOR)
        else:
            print 'Image registration mode is not supported!'

        if not self.device.getDepthColorSyncEnabled():
            self.device.setDepthColorSyncEnabled(True)

        self.color = VideoStream()
        self.depth = VideoStream()

        rc = self.color.create(self.device, SENSOR_COLOR)
        if rc != OPENNI_STATUS_OK:
            raise KinectException('Color stream create failed.')

        rc = self.depth.create(self.device, SENSOR_DEPTH)
        if rc != OPENNI_STATUS_OK:
            raise KinectException('Depth stream create failed.')

        #initialise kinect sensor signal recorder
        self.recorder = Recorder()
        if self.capture_raw:
            rc = self.recorder.create(self.out_raw_file_path)
            if rc != OPENNI_STATUS_OK:
                raise KinectException('Recorder create failed.')
            if not self.recorder.isValid():
                raise KinectException("Recorder invalid.")
            rc = self.recorder.attach(self.color, True)
            if rc != OPENNI_STATUS_OK:
                raise KinectException("Recorder attach color error.")
            rc = self.recorder.attach(self.depth, True)
            if rc != OPENNI_STATUS_OK:
                raise KinectException("Recorder attach depth error.")
            rc = self.recorder.start()
            if rc != OPENNI_STATUS_OK:
                raise KinectException("Recorder start error.")
            
        #initialise online algorithms recorder
        if self.capture_algs:
            self.out_algs_file = open(self.out_algs_file_path, 'wb')

        if self.mode == 'offline':
            self.playback = self.device.getPlaybackControl()
            if self.playback.isValid():
                self.playback.setRepeatEnabled(False)

        # initialise online hands tracker
        if self.track_hands:
            self.ht = HandTracker()
            rc = self.ht.create(self.device)
            if rc != NITE_STATUS_OK:
                raise KinectException('Creating hand tracker failed.')
                self.finish()
            self.ht.startGestureDetection(GESTURE_WAVE)
            self.ht.startGestureDetection(GESTURE_CLICK)
            self.ht.startGestureDetection(GESTURE_HAND_RAISE)

        # initialise online skeleton tracker
        if self.track_skeleton:
            self.ut = UserTracker()
            rc = self.ut.create()
            if rc != NITE_STATUS_OK:
                raise KinectException('Creating user tracker failed, ' + str(rc))
                self.finish()

        if self.ready_cb is not None:
            self.ready_cb()

        s = Serialization()
        s.register_hand_coordinates(lambda x, y, z: self.ht.convertHandCoordinatesToDepth(x, y, z))
        s.register_joint_coordinates(lambda x, y, z: self.ut.convertJointCoordinatesToDepth(x, y, z))

        rc = self.depth.start()
        if rc != OPENNI_STATUS_OK:
            raise KinectException('Depth stream start failed.')
            self.depth.destroy()

        rc = self.color.start()
        if rc != OPENNI_STATUS_OK:
            raise KinectException('Color stream start failed.')
            self.color.destroy()

        frame_index = 0
        cfi = None # current frame index
        last_cfi = None
        self.time_rec_start = time.time()
        
        color_start_frame_index = None 
        depth_start_frame_index = None 
        
        while True:
            k = cv2.waitKey(1)
            if self.loop_cb is not None:
                if self.loop_cb(k):
                    break

            rc, self.color_frame = self.color.readFrame()
            if rc != OPENNI_STATUS_OK:
                print 'Error reading color frame.'

            rc, self.depth_frame = self.depth.readFrame()
            if rc != OPENNI_STATUS_OK:
                print 'Error reading depth frame.'

            if color_start_frame_index is None:
                color_start_frame_index = self.color_frame.frameIndex
            if depth_start_frame_index is None:
                depth_start_frame_index = self.depth_frame.frameIndex

            frame_index = self.depth_frame.frameIndex - depth_start_frame_index
                
            if self.color_frame is not None and self.color_frame.isValid():
                data_rgb = self.color_frame.data
                data_rgb = cv2.cvtColor(data_rgb, cv2.COLOR_BGR2RGB)

            if self.depth_frame is not None and self.depth_frame.isValid():
                data_depth = self.depth_frame.data
                data_depth = np.float32(data_depth)
                data_depth = data_depth * (-255.0/3200.0) + (800.0*255.0/3200.0)
                data_depth = data_depth.astype('uint8')
                data_depth = cv2.cvtColor(data_depth, cv2.COLOR_GRAY2RGB)

            # compute and display current hands
            if self.track_hands:
                rc, self.hand_frame = self.ht.readFrame()
                if rc != NITE_STATUS_OK:
                    print 'Error reading hand tracker frame'
                for g in self.hand_frame.gestures:
                    if g.isComplete():
                        rc, newId = self.ht.startHandTracking(g.currentPosition)
                self.hands = self.hand_frame.hands
                if self.show_hands:
                    self.draw_hands(data_depth, self.hands)
                    self.draw_hands(data_rgb, self.hands)

            # compute and display current skeleton
            if self.track_skeleton:
                rc, self.user_frame = self.ut.readFrame()
                if rc != OPENNI_STATUS_OK:
                    print 'Error reading user tracker frame'
                self.users = self.user_frame.users
                for u in self.users:
                    if u.isNew():
                        self.ut.startSkeletonTracking(u.id)
                    elif u.skeleton.state == SKELETON_TRACKED and self.show_skeleton:
                        self.draw_user(data_rgb, u.skeleton)
                        self.draw_user(data_depth, u.skeleton)

            # capture hands and/or skeleton to file (in online mode only)
            if self.capture_algs:
                if self.capture_hands and self.capture_skeleton:
                    #print("1 " + str(self.color_frame.frameIndex) + " / " + str(self.depth_frame.frameIndex) + " / " + str(self.hand_frame.frameIndex) + " / " + str(self.user_frame.frameIndex))
                    #print("11 " + str(self.color_frame.timestamp) + " / " + str(self.depth_frame.timestamp) + " / " + str(self.hand_frame.timestamp) + " / " +  str(self.user_frame.timestamp))
                    header = [frame_index, 1, 1, time.time()]
                    header += self.get_frames()
                    self.out_algs_file.write(s.serialize_frame(header, self.hand_frame, self.user_frame, frame_index))
                elif self.capture_hands:
                    header = [frame_index, 0, 1, time.time()]
                    header += self.get_frames()
                    self.out_algs_file.write(s.serialize_frame(header, self.hand_frame, None, frame_index))
                elif self.capture_skeleton:
                    header = [frame_index, 1, 0, time.time()]
                    header += self.get_frames()
                    self.out_algs_file.write(s.serialize_frame(header, None, self.user_frame, frame_index))
                else:
                    header = [frame_index, 0, 0, time.time()]
                    header += self.get_frames()
                    self.out_algs_file.write(s.serialize_frame(header, None, None, frame_index))
            
            # show raw signal (from file or sensor) and skeleton/hands from file (if offline mode)
            if self.show_rgb:
                if self.mode == 'offline':
                    #print("01 " + str(self.color_frame.frameIndex) + " / " + str(self.depth_frame.frameIndex))
                    #print("011" + str(self.color_frame.timestamp) + " / " + str(self.depth_frame.timestamp))
                    rfi = int(0.5*(self.depth_frame.frameIndex + self.color_frame.frameIndex) + 0.5) # real frame index (for ONI data)
                    if self.show_skeleton or self.show_hands:
                        if cfi is None:
                            data = s.unserialize_frame(self.in_algs_file)
                            if data:
                                cfi = data[0] # rgb frame index (for hands and skeleton)                           
                        while rfi > cfi:
                            data = s.unserialize_frame(self.in_algs_file)
                            if not data:
                                break
                            cfi = data[0] # rgb frame index (for hands and skeleton)
                        if not data:
                            print 'END OF DATA'
                            break

                        #print 'rfi, cfi', rfi, cfi
                        self.draw_from_file(data, data_rgb)
                        cv2.imshow('color', data_rgb)             
                    else: # show only rgb offline
                        cv2.imshow('color', data_rgb)
                else: # online mode
                    cv2.imshow('color', data_rgb)
            if self.show_depth:
                cv2.imshow('depth', data_depth)
        print 'main loop finished'
        self.finish()


if __name__ == '__main__':
    try:
        mode = sys.argv[1]
    except Exception:
        mode = 'online'
    kinect = KinectAmplifier({'mode': mode})
    kinect.run()
