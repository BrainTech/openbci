#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import sys, os.path, time

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils import streaming_debug
from obci.utils.openbci_logging import log_crash

DEBUG = True

class SignalReceiver(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(SignalReceiver, self).__init__(addresses=addresses,
                                          type=peers.SIGNAL_STREAMER)
        if DEBUG:
            self.debug = streaming_debug.Debug(
                int(self.config.get_param('sampling_rate')),
                self.logger,
                int(self.config.get_param('samples_per_packet')))

        amp_saw = self.config.get_param('amp_saw')
        driver_saw = self.config.get_param('driver_saw')
        active_channels = self.config.get_param('active_channels').split(';')
        self.driver_saw_ind = -1
        self.amp_saw_ind = -1
        self.driver_saw_max = float(self.config.get_param('driver_saw_max'))
        self.amp_saw_max = float(self.config.get_param('amp_saw_max'))
        self.driver_saw_step = float(self.config.get_param('driver_saw_step'))
        self.amp_saw_step = float(self.config.get_param('amp_saw_step'))
        self._amp_saw_last = 0.0
        self._driver_saw_last = 0.0
        try:
            self.driver_saw_ind = active_channels.index(driver_saw)
        except:
            self.logger.info("NO driver saw!")
        try:
            self.amp_saw_ind = active_channels.index(amp_saw)
        except:
            self.logger.info("NO amp saw!")            

        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            if DEBUG:
                self.debug.next_sample()
            msg = mxmsg.message
            l_vec = variables_pb2.SampleVector()
            l_vec.ParseFromString(msg)
            self.logger.debug("Got pack of samples in moment: "+str(time.time()))
            for i_sample in l_vec.samples:
                diff = time.time()-i_sample.timestamp
                comm = ''.join([
                        "Sample ts: ", str(i_sample.timestamp),
                        " / Real ts:"+str(time.time()),
                        " / "+"DIFF: "+str(diff)])
                self.logger.debug(comm)
                if diff > 0.1:
                    self.logger.error(comm+"\n\n")
                if self.amp_saw_ind >= 0:
                    v = i_sample.channels[self.amp_saw_ind]
                    if self._amp_saw_last + self.amp_saw_step - v > 0:
                        self.logger.error("Last: "+str(self._amp_saw_last)+" Amp saw: "+str(v))
                        self.logger.error(''.join(["LOOOOOOOOST AMPLIFIER SAMPLES, sth like: ",
                                              str(self._amp_saw_last + self.amp_saw_step - v),
                                              " samples!!!"
                                              ])+"\n\n")

                    if v == self.amp_saw_max:
                        self._amp_saw_last = -self.amp_saw_step + 1
                    else:
                        self._amp_saw_last = v
                    self.logger.debug("Amp saw: "+str(v))
                if self.driver_saw_ind >= 0:
                    v = i_sample.channels[self.driver_saw_ind]
                    if self._driver_saw_last + self.driver_saw_step - v > 0:
                        self.logger.error("Last: "+str(self._driver_saw_last)+" Driver saw: "+str(v))
                        self.logger.error(''.join(["LOOOOOOOOST DRIVER SAMPLES, sth like: ",
                                              str(self._driver_saw_last + self.driver_saw_step - v),
                                              " samples!!!"
                                              ])+"\n\n")

                    if v == self.driver_saw_max:
                        self._driver_saw_last = -self.driver_saw_step + 1
                    else:
                        self._driver_saw_last = v
                    self.logger.debug("Driver saw: "+str(v))
                self.logger.debug("First channel value: "+str(i_sample.channels[0]))
        else:
            self.logger.error("Got unrecognised message!!!")
        self.no_response()

if __name__ == "__main__":
    SignalReceiver(settings.MULTIPLEXER_ADDRESSES).loop()



