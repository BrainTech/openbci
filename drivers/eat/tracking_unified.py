#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time
import sys, signal
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

#from tobii import eye_tracking_io
#import tobii.eye_tracking_io.eyetracker
#import tobii.eye_tracking_io.mainloop
#import tobii.eye_tracking_io.browsing
#import tobii.eye_tracking_io.types

#dummy import when no access to a real eyetracker
import eye_tracking_io.eyetracker
import eye_tracking_io.mainloop
import eye_tracking_io.browsing
import eye_tracking_io.types

from obci.configs import settings, variables_pb2
import logging
import threading

class EtrAmplifierTobii(ConfiguredClient):
    @staticmethod
    def extract_channels(d):
        return [d.LeftEyePosition3D.x, d.LeftEyePosition3D.y, d.LeftEyePosition3D.z,
            d.LeftEyePosition3DRelative.x, d.LeftEyePosition3DRelative.y, d.LeftEyePosition3DRelative.z,
            d.LeftGazePoint3D.x, d.LeftGazePoint3D.y, d.LeftGazePoint3D.z,
            d.LeftGazePoint2D.x, d.LeftGazePoint2D.y,
            d.LeftPupil,
            float(d.LeftValidity),
            d.RightEyePosition3D.x, d.RightEyePosition3D.y, d.RightEyePosition3D.z,
            d.RightEyePosition3DRelative.x, d.RightEyePosition3DRelative.y, d.RightEyePosition3DRelative.z,
            d.RightGazePoint3D.x, d.RightGazePoint3D.y, d.RightGazePoint3D.z,
            d.RightGazePoint2D.x, d.RightGazePoint2D.y,
            d.RightPupil,
            float(d.RightValidity)
        ]
    
    def __init__(self, addresses):
        super(EtrAmplifierTobii, self).__init__(addresses=addresses, type=peers.AMPLIFIER)
        self.logger.info("Start initializing eat amplifier...")
        #....init etr
        self._init_signals()
        self.connector = TrackingConnector()
        self.ready()
        self.apply_calibration()
    
    def apply_calibration(self):
        calibration_data_path = self.get_param("calibration_data_path")
        if calibration_data_path:
            self.connector.upload_calibration(calibration_data_path)

    def _process_message(self, msg):
        self.logger.debug("ETR sending message...")
        self.conn.send_message(message = msg.SerializeToString(), 
                               type = types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
    
    def _init_signals(self):
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        
    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("Got signal " + str(signum) + "!!! TUrning etr off!")
            #self.conn.send_message(message="finish", type=types.ACQUISITION_CONTROL_MESSAGE)
            # some cleanup ...
            sys.exit(-signum)
        return handler
    
    def _gaze_to_packets(self, source):
        sample_count = 0
        packet = variables_pb2.SampleVector()
        samples_per_packet = int(self.get_param("samples_per_packet"))
        for gaze_data in source:
            sample = packet.samples.add()
            sample.timestamp = int(time.time())
            sample.channels.extend(self.extract_channels(gaze_data))
            sample_count += 1
            if sample_count == samples_per_packet:
                yield packet
                packet = variables_pb2.SampleVector()
                sample_count = 0
    
    def tracking(self):
        return self._gaze_to_packets(self.connector.tracking())
    
    def run(self):
        for sample_packet in self.tracking():
            self._process_message(sample_packet)


class DiscoveryContext(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.eyetracker_info = None


class ConnectionContext(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.eyetracker = None


class TrackingContext(object):
    def __init__(self):
        self.condition = threading.Condition()
        self.last_sample = None


class TrackingConnector(object):
    def __init__(self):
        self.logger = logging.getLogger("eat_amplifier")
        self.eyetracker = None
        self.eyetracker_info = None
        self.tracking_context = None
        eye_tracking_io.init()
        self._detect_eyetracker()
        self._connect_to_eyetracker()

    def _detect_eyetracker(self):
        mainloop = eye_tracking_io.mainloop.MainloopThread()
        context = DiscoveryContext()
        browser = eye_tracking_io.browsing.EyetrackerBrowser(mainloop, self.browsing_callback, context)
        with context.condition:
            context.condition.wait(7)
            #mainloop.stop()
            if context.eyetracker_info:
                self.eyetracker_info = context.eyetracker_info
            else:
                raise Exception("No eyetracker found")
        browser.stop()
    
    def browsing_callback(self, _id, message, eyetracker_info, *args):
        context = args[0]
        if message == 'Found':
            with context.condition:
                context.eyetracker_info = eyetracker_info
                context.condition.notify()
    
    def _connect_to_eyetracker(self):
        mainloop = eye_tracking_io.mainloop.MainloopThread()
        context = ConnectionContext()
        eye_tracking_io.eyetracker.Eyetracker.create_async(mainloop, self.eyetracker_info, self.connect_callback, context)
        with context.condition:
            context.condition.wait(7)
            if context.eyetracker:
                self.eyetracker = context.eyetracker
            else:
                raise Exception("Could not connect to eyetracker")
    
    def connect_callback(self, _error, eyetracker, context):
        with context.condition:
            context.eyetracker = eyetracker
            context.condition.notify()
    
    def tracking(self):
        try:
            self.tracking_context = TrackingContext()
            self.eyetracker.StartTracking(None)
            self.eyetracker.events.OnGazeDataReceived += self.tracking_handler
            while True:
                with self.tracking_context.condition:
                    self.tracking_context.condition.wait(0.03)
                    last_sample =  self.tracking_context.last_sample
                    self.tracking_context.last_sample = None
                if last_sample:
                    yield last_sample
        finally:
            self.eyetracker.events.OnGazeDataReceived -= self.tracking_handler
            self.eyetracker.StopTracking()
    
    def tracking_handler(self, _error, gaze):
        with self.tracking_context.condition:
            self.tracking_context.last_sample = gaze
            self.tracking_context.condition.notify()

    def upload_calibration(self, path):
        calibration_file = open(path, "rb")
        calibration = eye_tracking_io.converters.Calibration(calibration_file.read())
        self.eyetracker.SetCalibration(calibration)


if __name__ == "__main__":
    EtrAmplifierTobii(settings.MULTIPLEXER_ADDRESSES).run()
