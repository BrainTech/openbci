#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, os
import numpy as np

class EtrDecManager(object):
    def __init__(self, speller_area_count, buffer_size, ratio, stack, delay, dec_count, feed_fade, long_dec_delay):
        """self.configs = {
            'SPELLER_AREA_COUNT': None,
            
            # Samples buffer size. Should be large int value. 
            # It's responsible for latency at beggining (larger
            # value - longer latency) and mean values are 
            # determined from this stack (more samples - 
            # more accurate mean values)
            'ETR_BUFFER_SIZE': None,
            
            # Determines what values of 
            'ETR_NESW_RATIO': None,
            
            # How many last samples to take under account
            # when determint current ete retina posistion
            'ETR_NESW_STACK': None,

            #
            'ETR_NESW_DELAY': None,
            
            
            # Delay (in samples count) to be done after
            # decision is sent
            'ETR_NESW_DEC_COUNT': None,
            
            # When decision is made some blocks on ugm are
            # highlit. This constant describes fading progress - 
            # in how many sample_counts will the block gradually 
            # dim.
            'ETR_NESW_FEED_FADE': None
            }"""
        self.speller_area_count = int(speller_area_count)
        assert(self.speller_area_count > 0)
        
        self.ratio = float(ratio)
        assert( 0 < self.ratio < 1 )
        
        self.stack = int(stack)
        assert( self.stack > 0 )

        self.dec_count = int(dec_count)
        assert( self.dec_count > 0)
        assert( self.dec_count < self.stack )
        
        self.delay = int(delay)
        assert( self.delay > 0 )
        
        self.feed_fade = int(feed_fade)
        assert(self.feed_fade > 0)

        # Radius treshold
        self.rMin = np.zeros(4)
        self.xMin, self.yMin =  100, 100 # Random large value
        self.xMax, self.yMax = -100,-100 # Random small value
        
        # threshold ratio value
        self.st = self.ratio

        # Array's length
        self.nStackLength = self.stack
        self.nLastCorr = self.dec_count
        self.nFeedback = self.feed_fade

        self.stack = np.zeros((2,self.nStackLength))
        self.stack2 = np.zeros((2,self.nStackLength))

        # Feeds
        self.fading = 1./self.nFeedback
        self.feeds = [0]*self.speller_area_count

        # Decision
        self.decFlag = True
        self.decNDelay = self.delay
        self.longDecNDelay = int(long_dec_delay)
        self.longDecFlag = True
        self.lastDec = -1
        
        self.longNCount = 0
        self.nCount = 0

    def get_feedbacks(self, msg):
        """Fired every frame. Determine if (msg.x, msg.y) denotes 'moved'.
        Returns:
        - dec - decision (eg. if you have four decisions return 0 or 1 or 2 or 3 or -1(if no decision is made)
        - feeds - a list of floats in range [0;1] - 0 will result in no change in ugm, 1 will result in change
        of field`s colour. You should return '1' smartly - eg. if in time point T you return eg decision=2 then eg. for 
        5 subseqent time points (T+1, T+2 ...) you should return feeds like [0,0,1,0,0,0,...] so that user sees
        for at least few frames that he made a decision"""
        dec, feeds = -1, []

        print "{0:*^30}".format('NEW')
        print "x,y = ", msg.x, msg.y

        # 'inteligent' fading
        for p in self.feeds:
            if p<=self.fading: p = 0
            else:              p-= self.fading
            feeds.append( p )
        self.feeds = feeds
        
        
        # Dump x/y coordinates into stack.
        # Origin is in upper right corner thus
        # x/y are multiplied by -1 (-> origin = bottom left)
        tmp = np.array([msg.x,msg.y]).reshape(2,1)
        tmp *= -1
        self.stack = np.hstack((self.stack,tmp))[:,1:]
        if self.longDecFlag:
            self.stack2 = np.hstack((self.stack2,tmp))[:,1:]
                
        # Calculate mean values of x and y corrdinate
        xMean = self.stack2[0].mean()
        yMean = self.stack2[1].mean()
        mean = [xMean, yMean]
        print "mean: ", mean
        

        # Start algorithm only if buffer data is full.
        # Otherwise mean values aren't calculated properly
        if self.stack[0][0] == 0:
            if self.stack[0][1] == 0:
                dec = 0
            else:
                dec = 5
                feeds = [1]*6
            return dec, feeds


        # Look for min/max values in stack
        st = self.st
        xMin, xMax = self.stack[0].min(), self.stack[0].max()
        yMin, yMax = self.stack[1].min(), self.stack[1].max()
        
        # Compare them with min/max values ever
        if xMin < self.xMin: self.xMin = xMin
        if xMax > self.xMax: self.xMax = xMax
        if yMin < self.yMin: self.yMin = yMin
        if yMax > self.yMax: self.yMax = yMax
        
        # Threshold value is 'st' ratio of distance
        # between mean value and min/max value
        self.rMin[0] = (self.xMin - xMean)*st
        self.rMin[1] = (self.xMax - xMean)*st
        self.rMin[2] = (self.yMin - yMean)*st
        self.rMin[3] = (self.yMax - yMean)*st
        print "self.rMin: ", self.rMin
        
        # Makes a delay of decNDelay turns
        # after make a decision
        if not self.decFlag:
            self.nCount += 1
            if self.nCount == self.decNDelay:
                self.decFlag = True
                self.nCount = 0
            return dec, feeds
        
        

        # For each direction check if average nLastCorr 
        # x or y samples was greater then threshold for that
        # direction. If so, return that direction in decision. 
        for i in range(4):
            m = mean[i/2]
            v = self.stack[i/2,-self.nLastCorr:].mean()
            val = v - m
            #~ print "{0}. {1} = {2} - {3}".format(i,val,v,m)
            if (val-self.rMin[i])*(-1)**i < 0: 
                if dec<0: 
                    dec = i
                    if self.lastDec == dec:
                        self.longDecFlag = False # Sets on delay flag
                    else:
                        self.longDecFlag = True
                        self.longNCount = 0
                        self.lastDec = -1
                    break
                
        if dec != -1:
            self.longNCount +=1
            print self.longNCount
            self.lastDec = dec
            if self.longNCount == self.longDecNDelay:
                self.longDecFlag = True
                self.decFlag = False
                self.longNCount = 0
            else:
                dec = -1
                return dec, feeds
        else:
            self.lastDec = -1
            self.longDecFlag = True
            self.longNCount = 0



        # If no decision was made (dec == -1)
        if dec < 0:
            return dec, feeds

        # Flashing feedback
        if dec == 0:
            self.feeds[0] = 1
            self.feeds[3] = 1
        elif dec==1:
            self.feeds[2] = 1
            self.feeds[5] = 1
        elif dec==2:
            self.feeds[3] = 1
            self.feeds[4] = 1
            self.feeds[5] = 1                        
        elif dec==3:
            self.feeds[0] = 1
            self.feeds[1] = 1
            self.feeds[2] = 1            


        feeds = self.feeds

        # END OF FUNCTION
        return dec, feeds
