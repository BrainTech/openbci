#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl> 
#     Marian Dovgialo <marian.dowgialo@gmail.com>
import time
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.gui.ugm import ugm_helper
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash
from obci.gui.ugm import ugm_config_manager

class LogicDecisionFeedbackBudzik(ConfiguredMultiplexerServer):
    '''Logic to controll N classes BCI
    The cartaker should ask a question and then press
    space to activate BCI. The BCI user should then concentrate on
    answer'''
    
    @log_crash
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(LogicDecisionFeedbackBudzik, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_FEEDBACK)

        self.feed_time = float(self.config.get_param('feed_time'))
        first_field_id = self.config.get_param('blink_ugm_id_start')
        #we need background field id which for id 1001 would be 10001:
        first_field_id = int(first_field_id[0] + '0' +first_field_id[1:])
        active_field_offsets = [int(i) for i in self.config.get_param('active_field_ids').split(';')]
        ugm_field_ids = [i+first_field_id for i in active_field_offsets]
        #~ self.dec_count = int(self.config.get_param('dec_count'))
        self.blinking_config = self.config.get_param('ugm_config')
        self.blinking_config_ugm = ugm_config_manager.UgmConfigManager(self.blinking_config).config_to_message()
        self.feed_manager = ugm_helper.UgmColorUpdater(
            self.blinking_config,
            ugm_field_ids
            )
        
        self.HELLO_MESSAGE = self.config.get_param('hello_message')
        assert(self.feed_time >= 0)
        #~ assert(self.dec_count > 0)
        self.ready()
        self.begin()


    def begin(self):
        ugm_helper.send_text(self.conn, self.HELLO_MESSAGE)
        time.sleep(5)
        ugm_helper.send_config(self.conn, self.blinking_config_ugm)
        #~ ugm_helper.send_start_blinking(self.conn)
        
    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            dec = int(mxmsg.message)
            self.logger.info("Got decision: "+str(dec))
            assert(dec >= 0)
            dec_time = time.time()
            self._send_feedback(dec, dec_time)
        elif mxmsg.type == types.UGM_ENGINE_MESSAGE:
            msg = variables_pb2.Variable()
            msg.ParseFromString(mxmsg.message)
            if msg.key == 'keybord_event':
                self.logger.info("Got keypress: {}".format(msg.value))
                if msg.value == '32':#space
                    ugm_helper.send_start_blinking(self.conn)
                    
        self.no_response()
    
    def _send_feedback(self, dec, dec_time):
        ugm_helper.send_stop_blinking(self.conn)
        while True:
            t = time.time() - dec_time
            if t > self.feed_time:
                ugm_config = self.feed_manager.update_ugm(dec, -1)
                ugm_helper.send_config(self.conn, ugm_config, 1)
                break
            else:
                self.logger.debug("t="+str(t)+"FEED: "+str(t/self.feed_time))
                ugm_config = self.feed_manager.update_ugm(dec, 1-(t/self.feed_time))
                ugm_helper.send_config(self.conn, ugm_config, 1)
                time.sleep(0.05)
        

if __name__ == "__main__":
    LogicDecisionFeedbackBudzik(settings.MULTIPLEXER_ADDRESSES).loop()

