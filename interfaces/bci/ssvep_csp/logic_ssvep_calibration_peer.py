#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path, sys, time, Queue, random

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_helper
from obci.devices import appliance_helper
from obci.utils import keystroke
from obci.utils import tags_helper
from obci.utils import sequence_provider

from obci.acquisition import acquisition_helper

class LogicSSVEPCalibration(ConfiguredClient):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicSSVEPCalibration, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_SSVEP_CALIBRATION)
        self.ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config")).config_to_message()
        self.raw_ugm = ugm_config_manager.UgmConfigManager(self.config.get_param("ugm_config"))
        self.text_ids = [int(i) for i in self.config.get_param("ugm_text_ids").split(';')]
        self.text_id = int(self.config.get_param('ugm_text_id'))
        self.hi_text = self.config.get_param("hi_text")
        self.bye_text = self.config.get_param("bye_text")
        self.trial_text = self.config.get_param("trial_text")
        self.ready_text = self.config.get_param("ready_text")
        self.break_texts = self.config.get_param("break_texts").split(';')
        self.break_times = [float(i) for i in self.config.get_param("break_times").split(';')]
        assert(len(self.break_texts)==len(self.break_times))
        self.target_time = float(self.config.get_param("target_time"))
        self.target_fancy = int(self.config.get_param("target_fancy"))
        self.feed_time = float(self.config.get_param("feed_time"))
        self.feed_text = self.config.get_param("feed_text")
        self._init_sequence()

        self._curr_fancy_x = 0.4
        self._curr_fancy_y = 0.4

        self.ready()

    def _init_sequence(self):
        #Number of fileds in gui - number of freqs one at the time
        fields_count = int(self.config.get_param("fields_count"))

        #Number of trials for every target freq
        target_count = int(self.config.get_param("target_count"))

        #A list of lists of freqs, from which target freq and 'non-target' freqs will be generated
        freqs = []
        for f in self.config.get_param("freqs").split(';'):
            f_list =self.config.get_param(f).split(';')
            if len(f_list) < fields_count:
                raise Exception("One of freqs list is smaller than fields_count. That can`t be!!!")
            freqs.append(f_list)
            
        self.all_freqs = sum(freqs, [])

        #An index of target field - migh be a number or literal representing 'method of generation', eg. random
        target_ind = self.config.get_param("target_ind")
        try:
            const = int(target_ind)
            target_ind_provider = sequence_provider.PROVIDERS['constant'](const)
        except ValueError:
            #target_ind isnt a number - assume it is CORRECT sequenc provider literal
            try:
                target_ind_provider = sequence_provider.PROVIDERS[target_ind](0, fields_count)
            except KeyError:
                self.logger.error("Incorrect target_id param. Cant find "+target_id+" sequence provieder!!!")
                sys.exit(1)

        #A list of (assumingly field_count-1) freqs for 'non-target' freqs or 'random' literal
        #meaning that we will select randomly non-target freqs
        non_target_freqs = self.config.get_param("non_target_freqs")
        if non_target_freqs != 'random':
            non_target_freqs = non_target_freqs.split(';')
            if len(non_target_freqs)!=fields_count-1:
                raise Exception("Number of non target freqs should be "+str(fields_count-1)+" as fields_count is "+str(fields_count))

        self.sequence = Queue.Queue()
        for f_list in freqs:# f_list is a list of frequencies 
            sequence_values = []
            for target in f_list: # target is a simple frequency (of string type, not float)
                if non_target_freqs == 'random':
                    other_freqs = list(f_list)
                    other_freqs.remove(target) #we don`t want target freq in non-target freqs of course ...
                    for i in range(target_count): #target must occure in target_count trials 
                        random.shuffle(other_freqs)
                        target_ind = target_ind_provider.get_value()
                        if len(other_freqs) >= fields_count:
                            ret_freqs = list(other_freqs[:fields_count])
                            ret_freqs[target_ind] = target
                        else:
                            ret_freqs = list(other_freqs)
                            ret_freqs.insert(target_ind, target)
                        sequence_values.append((ret_freqs, target_ind))
                else: #non_target_freqs is a list of fields_count-1 non-target freqs
                    for i in range(target_count):
                        target_ind = target_ind_provider.get_value()
                        ret_freqs = list(non_target_freqs)
                        ret_freqs.insert(target_ind, target)
                        sequence_values.append((ret_freqs, target_ind))
            random.shuffle(sequence_values) #we don`t want one target freq to occur in a sequence - shuffle it
            for v in sequence_values:
                self.logger.debug("SEQUENCE: "+str(v))
                self.sequence.put(v)
            self.logger.info("SEQUENCE - number of trials for freqs: "+str(f_list))
            self.logger.info(len(sequence_values))
        self.logger.info("SEQUENCE - number of all trials: "+str(self.sequence.qsize()))
        
        
    def run(self):
        self.logger.info("RUN!!!")
        #process intro
        #ugm_helper.send_text(self.conn, self.hi_text)
        ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.hi_text)
        #keystroke.wait([" "])
        time.sleep(20)
        #ugm_helper.send_text(self.conn, self.trial_text)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.trial_text)
        time.sleep(20)
        #keystroke.wait([" "])
        ugm_helper.send_config(self.conn, self.ugm)
        appliance_helper.send_freqs(self.conn, self.all_freqs[:int(self.config.get_param("fields_count"))])
        #ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_ids[1], 'message', self.feed_text)
        time.sleep(self.target_time)
        appliance_helper.send_stop(self.conn)
        #ugm_helper.send_text(self.conn, self.ready_text)
        ugm_helper.send_config(self.conn, self.ugm)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.ready_text)
        time.sleep(20)
        #keystroke.wait([" "])
        self.logger.info("Send begin config ...")
        #ugm_helper.send_config(self.conn, self.ugm)

        #process trials
        self._run()

        #process good bye
        appliance_helper.send_stop(self.conn)
        #ugm_helper.send_text(self.conn, self.bye_text)
        ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.bye_text)
        #acquire some more data
        time.sleep(2)
        self.logger.info("Send finish saving and finish ...")
        acquisition_helper.send_finish_saving(self.conn)

    def _run(self):
        self._send_exp_info()
        while True:
            try:
                freqs, target_ind = self.sequence.get_nowait()
            except:
                # sequence empty
                return
            self.logger.debug("NExt freqs: "+str(freqs)+" and target_ind: "+str(target_ind))
            self._send_ugm()
            self._send_feed(target_ind)
            self._send_freqs(freqs, target_ind)
            self._send_breaks()

    def _send_exp_info(self):
        desc = dict(self.config.param_values())
        desc['all_freqs'] = ';'.join(self.all_freqs)

        t = time.time()
        tags_helper.send_tag(
            self.conn, t, t, 
            "experimentInfo",
            desc)
        
    def _send_ugm(self):
        ugm_helper.send_config(self.conn, self.ugm)        
        t = time.time()
        tags_helper.send_tag(self.conn, t, t, "trial",{'duration':self.feed_time+self.target_time})

    def _send_feed(self, target_ind):
        if self.feed_time <= 0:
            return
        #prepare and send feed text
        l_config = [{'id':self.text_ids[target_ind],
                  'message':self.feed_text}]
        l_str_config = str(l_config)
        ugm_helper.send_config(self.conn, l_str_config, 1)
        t = time.time()
        tags_helper.send_tag(self.conn, t, t, "feedback",
                             {'field':target_ind,
                              'duration':self.feed_time
                              })
        #wait
        time.sleep(self.feed_time)

        #remove feed
        l_config[0]['message'] = ""
        l_str_config = str(l_config)
        ugm_helper.send_config(self.conn, l_str_config, 1)

    def _send_freqs(self, freqs, target_ind):
        appliance_helper.send_freqs(self.conn, freqs)
        t = time.time()
        tags_helper.send_tag(self.conn, t, t, "diodes",
                             {'freq':freqs[target_ind],
                              'freqs':freqs,
                              'field':target_ind,
                              'duration':self.target_time
                              })
        if self.target_fancy:
            self._send_fancy_target(target_ind)
        else:
            time.sleep(self.target_time)

    def _send_fancy_target(self, target_ind):
        t = time.time()
        target_config = str([self.raw_ugm.get_config_for(self.text_ids[target_ind])])
        while time.time() - t < self.target_time:
            self._curr_fancy_x += (random.random()-0.5)/25.0
            self._curr_fancy_y += (random.random()-0.5)/25.0
            if self._curr_fancy_x < 0.4:
                self._curr_fancy_x = 0.4
            elif self._curr_fancy_x > 0.6:
                self._curr_fancy_x = 0.6
            if self._curr_fancy_y < 0.4:
                self._curr_fancy_y = 0.4
            elif self._curr_fancy_y > 0.6:
                self._curr_fancy_y = 0.6
            l_str_config = str([
                {'id':self.text_ids[target_ind],
                 'message':self.feed_text,
                 'position_horizontal_type':'relative',
                 'position_vertical_type':'relative',
                 'position_horizontal':self._curr_fancy_x,
                 'position_vertical':self._curr_fancy_y,
                 #'font_size':15,
                 'message':self.feed_text
                 }
                ])
            ugm_helper.send_config(self.conn, l_str_config, 1)
            time.sleep(0.1)
        ugm_helper.send_config(self.conn, target_config, 1)
            

    def _send_breaks(self):
        t = time.time()
        tags_helper.send_tag(self.conn, t, t, "break",{'duration':sum(self.break_times)})
        appliance_helper.send_stop(self.conn)        
        for i, t in enumerate(self.break_times):
            #ugm_helper.send_text(self.conn, self.break_texts[i])
            ugm_helper.send_config_for(self.conn, self.text_id, 'message', self.break_texts[i]+str(self.sequence.qsize()))
            time.sleep(t)

if __name__ == "__main__":
    LogicSSVEPCalibration(settings.MULTIPLEXER_ADDRESSES).run()
