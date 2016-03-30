#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from collections import deque
import numpy as np

TEST_MODE = False
TEST_MODE_TIME = None


FRACTION_WAIT_COUNT = 10

class EtrDecManager(object):
    def __init__(self, dec_type, push_dec_count, push_feed_count, buffer_size, 
                 ignore_missed, speller_area_count, dec_break):

        self.ignore_missed = int(ignore_missed)
        self.buffer_size = float(buffer_size)
        self.dec_type = dec_type
        if dec_type == 'count':
            self.push_feed_count = int(push_feed_count)
            self.push_dec_count = int(push_dec_count)
        elif dec_type == 'fraction':
            self.push_feed_count = float(push_feed_count)
            self.push_dec_count = float(push_dec_count)
        else:
            raise Exception("Unrecognised ETR_DEC_TYPE = "+dec_type)
        assert(self.push_dec_count > 0)
        assert(self.push_feed_count < self.push_dec_count)
        self.speller_area_count = int(speller_area_count)
        assert(self.speller_area_count > 0)
        self.dec_break = float(dec_break)

        self.initValues()

        self.last_tss = []
        self.last_dec = 0
        for i in range(self.speller_area_count+1):
            self.last_tss.append(deque())
        

    def initValues(self):
        # Transformation matrix
        self.invS = np.eye(3)
        
        self.scaleValue = 1.        

    def getRealData(self, msg):
        x, y = msg.x, msg.y
        print "{},{}".format(x, y)
        Xp = np.matrix( [x, y,1]).T
        X = self.invS*Xp
        print "newX: ", X
        msg.x, msg.y = float(X[0]), float(X[1])
        
        # Should it return anything?
        # Cuz this only changes values inside object
        return msg
        

    def updateTransformationMatrix(self, data):
        print "\n"*5
        print "dostalem: ", data
        print "\n"*5
        data = np.array(data)
        data = data*self.scaleValue
        invS = np.array( data).reshape((3,3))
        #~ S = np.random.random( (3,3))
        #~ invS = np.linalg.inv(S)
        self.invS = np.matrix(invS)
        
        print "self.invS: ", self.invS
        

    def area_pushed(self, area_id, msg):
        """Fired every 'tick'.
        area_id is either -1 (no are is being pushed)
        or 0 < area_id < self.configs['SPELLER_AREA_COUNT'].
        Update internal data structures with area_id and current time.
        """
        if time.time() - self.last_dec < self.dec_break:
            return
        if area_id >= 0:
            self.last_tss[area_id].appendleft(msg.timestamp)
        else:
            self.last_tss[self.speller_area_count].appendleft(msg.timestamp)

        self._update_tick()

    def _update_tick(self):
        """Fired every tick.
        Remove all 'outdated' timestamps for every area regarding ETR_BUFFER_SIZE."""
        if TEST_MODE:
            t = TEST_MODE_TIME
        else:
            t = time.time()

        brink_t = t - self.buffer_size
        for tss in self.last_tss:
            while True:
                try:
                    v = tss.pop()
                    #print("v < brink_t? = "+str(v)+" < "+str(brink_t))
                    if  v >= brink_t:
                        tss.append(v)
                        break
                    # else v timestamp is too old - throw it away
                except IndexError:
                    break

    def _reset_tss(self):
        self.last_dec = time.time()
        for q in self.last_tss:
            q.clear()
        
    def get_feedbacks(self):
        dec = -1
        feeds = [0]*self.speller_area_count
        if time.time() - self.last_dec < self.dec_break:
            return dec, [0.01]*self.speller_area_count

        feed_scale = float(self.push_dec_count - self.push_feed_count)
        #print('feed_scale: '+str(feed_scale))

        if self.dec_type == 'count':
            for i in range(len(feeds)):
                count = len(self.last_tss[i])
                #print("Tss count for "+str(i)+" = "+str(count))
                if count >= self.push_dec_count:
                    feeds[i] = 1.0
                    dec = i
                    break
                elif count > self.push_feed_count:
                    feeds[i] = (count - self.push_feed_count)/feed_scale
                else:
                    feeds[i] = 0.0
        else: # == 'FRACTION'
            x = 0
            if self.ignore_missed:
               x = 1
            all_count = sum([len(self.last_tss[i]) for i in range(len(self.last_tss)-x)])
            for i in range(len(feeds)):
                if all_count < FRACTION_WAIT_COUNT:
                    fract = 0
                else:
                    fract = len(self.last_tss[i])/float(all_count)
                if fract >= self.push_dec_count:
                    feeds[i] = 1.0
                    dec = i
                    break
                elif fract > self.push_feed_count:
                    feeds[i] = (fract - self.push_feed_count)/feed_scale
                else:
                    feeds[i] = 0.0

        if dec >= 0:
            self._reset_tss()
        return dec, feeds


        """self.configs = {
            # enumerator {'COUNT', 'FRACTION'}:
            # - COUNT means that decision is made by considering 'how many times the area has been pushed'
            # - FRACTION means that decision is made by considering 'what is the fraction of a number times given ara has been pushed 
            #   in relation to a number of times all areas has been pushed
            # in practice FRACTION mode is independent of etr sampling frequency; using COUNT mode you need to know the sampling frequency
            'ETR_DEC_TYPE':None,

            # Above this value it is considered that an area is pushed (the decision has been made)
            # In COUNT mode it should be some natural number (eg. 20 denotes that if in previous ETR_BUFFER_SIZE seconds given
            # field has been pushed more than 20 times it means that the user really want to push it.)
            # In FRACTION mode it should be float in [0;1] range (eg. 0.4 denotes that if in previous ETR_BUFFER_SIZE seconds given
            # field has been pushed more than 40% times it means that the user really want to push it.)
            'ETR_PUSH_DEC_COUNT':None, 

            # This is simillar to ETR_PUSH_DEC_COUNT, above this value area is considered to be 'interesting' for the user
            # and the user should be given a feedback
            'ETR_PUSH_FEED_COUNT':None,

            # How many previous seconds should be taken into consideration
            'ETR_BUFFER_SIZE':None,

            # enumerator { 1(True), 0(False)}
            # Used in FRACTION mode, if true than 'missed' hits are ignored, otherwise counted.
            # Eg. having areas 1,2 if the user pushed 1-st area 3 times and 2-nd area 2 times and 
            # pushed 'background' (area somewhere beyound areas 1 and 2) 10 times then:
            # if ETR_IGNORE_MISSED == True then fraction(area1) == 3/(3+2+10) and fraction(area2) == 2/(3+2+10)
            # if ETR_IGNORE_MISSED == False then fraction(area1) == 3/(3+2) and fraction(area2) == 2/(3+2)
            'ETR_IGNORE_MISSED':None,

            'SPELLER_AREA_COUNT': None,

            'ETR_DEC_BREAK':None,

            }"""
