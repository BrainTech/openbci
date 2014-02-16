#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from KinectUtils import Serialization

class KinectDataReader(object):
    def __init__(self, file_name):
        super(KinectDataReader, self).__init__()
        self.file_name = file_name
        self.in_algs_file = open(self.file_name + '.algs', 'rb')
        self._s = Serialization()

    def readNextFrame(self):
        return self._s.unserialize_frame(self.in_algs_file)


if __name__ == '__main__':
    try:
        file_name = sys.argv[1]
    except Exception:
        file_name = 'test'
    kinect = KinectDataReader(file_name)
    while True:
        frame = kinect.readNextFrame()
        if frame is None:
            print('END OF FILE')
            break

        frame_index = frame[0]
        hands_included = frame[1]
        skeleton_included = frame[2]
        frame_time = frame[3]

        if skeleton_included:
            skel = frame[8]
        else:
            skel = None

        if hands_included:
            hands = frame[9]
        else:
            hands = None
                    
        print('Idx:', frame_index, 'Time:', frame_time)
        if skel is not None:
            print('Skel: ', skel.user_x, skel.user_y, skel.user_z)

        if hands is not None:
            print('Hands: ', hands.hands[0].x, hands.hands[0].y, hands.hands[0].z)

