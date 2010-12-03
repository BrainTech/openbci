import math, time, random
import numpy as np
import threading


class DataGenerator( threading.Thread ):
   
    def __init__(self):
       self.bufferSize = 1024
       self.samplingRate = 128
       
       self.buffer = np.zeros( (self.bufferSize,2), float)
       
    def func(self, t):
        return math.sin(t*2) + math.cos(t*4)/2 + random.random()-0.5
        
    def run(self):
        while(1):
            self.buffer[:-1] = self.buffer[1:]
            t = time.time()
            self.buffer[-1] = np.array((t,self.func(t)))
            time.sleep(1.0/self.samplingRate)
            print "a"




