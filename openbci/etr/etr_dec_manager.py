#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from collections import deque

TEST_MODE = False
TEST_MODE_TIME = None


FRACTION_WAIT_COUNT = 10

class EtrDecManager(object):
    def __init__(self):
        self.configs = {
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

            }
    def get_requested_configs(self):
        return self.configs.keys()

    def set_configs(self, configs):
        for k in self.configs.keys():
            self.configs[k] = configs[k] #assumed all keys in self.configs are in configs
        self._assert_configs()
        self._init_configs()

    def _assert_configs(self):
        """Fired after setting configs from system settings.
        Assure configs are correct, change config type if needed 
        (system setting are always as strings)."""
        self.configs['ETR_IGNORE_MISSED'] = int(self.configs['ETR_IGNORE_MISSED'])
        self.configs['ETR_BUFFER_SIZE'] = float(self.configs['ETR_BUFFER_SIZE'])
        if self.configs['ETR_DEC_TYPE'] == 'COUNT':
            self.configs['ETR_PUSH_FEED_COUNT'] = int(self.configs['ETR_PUSH_FEED_COUNT'])
            self.configs['ETR_PUSH_DEC_COUNT'] = int(self.configs['ETR_PUSH_DEC_COUNT'])
        elif self.configs['ETR_DEC_TYPE'] == 'FRACTION':
            self.configs['ETR_PUSH_FEED_COUNT'] = float(self.configs['ETR_PUSH_FEED_COUNT'])
            self.configs['ETR_PUSH_DEC_COUNT'] = float(self.configs['ETR_PUSH_DEC_COUNT'])
        else:
            raise Exception("Unrecognised ETR_DEC_TYPE = "+self.configs['ETR_DEC_TYPE'])
        assert(self.configs['ETR_PUSH_FEED_COUNT'] > 0)
        assert(self.configs['ETR_PUSH_FEED_COUNT'] < self.configs['ETR_PUSH_DEC_COUNT'])

        self.configs['SPELLER_AREA_COUNT'] = int(self.configs['SPELLER_AREA_COUNT'])
        assert(self.configs['SPELLER_AREA_COUNT'] > 0)

        self.configs['ETR_DEC_BREAK'] = float(self.configs['ETR_DEC_BREAK'])

    def _init_configs(self):
        """Fired after set_configs,
        init all needed data structures."""
        self.last_tss = []
        self.last_dec = 0
        for i in range(self.configs['SPELLER_AREA_COUNT']+1):
            self.last_tss.append(deque())

    def area_pushed(self, area_id, msg):
        """Fired every 'tick'.
        area_id is either -1 (no are is being pushed)
        or 0 < area_id < self.configs['SPELLER_AREA_COUNT'].
        Update internal data structures with area_id and current time.
        """
        if time.time() - self.last_dec < self.configs['ETR_DEC_BREAK']:
            return
        if area_id >= 0:
            self.last_tss[area_id].appendleft(msg.timestamp)
        else:
            self.last_tss[self.configs['SPELLER_AREA_COUNT']].appendleft(msg.timestamp)

        self._update_tick()

    def _update_tick(self):
        """Fired every tick.
        Remove all 'outdated' timestamps for every area regarding ETR_BUFFER_SIZE."""
        if TEST_MODE:
            t = TEST_MODE_TIME
        else:
            t = time.time()

        brink_t = t - self.configs['ETR_BUFFER_SIZE']
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
        feeds = [0]*self.configs['SPELLER_AREA_COUNT']
        if time.time() - self.last_dec < self.configs['ETR_DEC_BREAK']:
            return dec, [0.01]*self.configs['SPELLER_AREA_COUNT']

        feed_scale = float(self.configs['ETR_PUSH_DEC_COUNT'] - self.configs['ETR_PUSH_FEED_COUNT'])
        print('feed_scale: '+str(feed_scale))

        if self.configs['ETR_DEC_TYPE'] == 'COUNT':
            for i in range(len(feeds)):
                count = len(self.last_tss[i])
                print("Tss count for "+str(i)+" = "+str(count))
                if count >= self.configs['ETR_PUSH_DEC_COUNT']:
                    feeds[i] = 1.0
                    dec = i
                    break
                elif count > self.configs['ETR_PUSH_FEED_COUNT']:
                    feeds[i] = (count - self.configs['ETR_PUSH_FEED_COUNT'])/feed_scale
                else:
                    feeds[i] = 0.0
        else: # == 'FRACTION'
            x = 0
            if self.configs['ETR_IGNORE_MISSED']:
               x = 1
            all_count = sum([len(self.last_tss[i]) for i in range(len(self.last_tss)-x)])
            for i in range(len(feeds)):
                if all_count < FRACTION_WAIT_COUNT:
                    fract = 0
                else:
                    fract = len(self.last_tss[i])/float(all_count)
                if fract >= self.configs['ETR_PUSH_DEC_COUNT']:
                    feeds[i] = 1.0
                    dec = i
                    break
                elif fract > self.configs['ETR_PUSH_FEED_COUNT']:
                    feeds[i] = (fract - self.configs['ETR_PUSH_FEED_COUNT'])/feed_scale
                else:
                    feeds[i] = 0.0

        if dec >= 0:
            self._reset_tss()
        return dec, feeds
