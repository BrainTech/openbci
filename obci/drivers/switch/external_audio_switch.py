#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 1024*10
DTYPE = '<i2'

class AudioSwitch(object):
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                             channels=CHANNELS,
                             rate=RATE,
                             input=True,
                             frames_per_buffer=CHUNK)
        self.last = -1

    def next(self):
        data = self.stream.read(CHUNK)
        data = np.frombuffer(data, dtype=DTYPE)
        if np.shape(np.where(data > 20000)[0])[0] > 0 and self.last  != 0:
            self.last = 0
            return True
        if np.shape(np.where(data < -20000)[0])[0] > 0 and self.last != 1:
            self.last = 1

        return False

    def close(self):
        self.stream.close()
        self.p.terminate()


if __name__ == "__main__":
    s = AudioSwitch()
    while True:
        if s.next():
            print("DECISION!!!")
