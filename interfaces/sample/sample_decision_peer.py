#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import random, time, numpy

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci_configs import settings, variables_pb2

from interfaces import interfaces_logging as logger
#LOGGER = logger.get_logger("sample_analysis", "info")
LOGGER = logger.get_logger("sample_analysis", "debug")

class SampleAnalysis(ConfiguredMultiplexerServer):
    """A class responsible for handling signal message and making proper decision.
    The class inherits from generic class for convinience - all technical stuff
    is being done in this super-class"""
    def __init__(self, addresses):
        """Initialization - super() and ready() calls are required..."""
        super(SampleAnalysis, self).__init__(addresses=addresses,
                                          type=peers.ANALYSIS)
        self.ready()
        LOGGER.info("Sample analysis init finished!")

    def handle_message(self, mxmsg):
        """The only required function in the class
        that will be fired every time message is received"""
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            # Got proper message, let`s unpack it ...

            # Messages are transmitted in bunches so lets define SampleVector
            # in order to unpack bunch of Sample messages ...
	    l_vect = variables_pb2.SampleVector()
            l_vect.ParseFromString(mxmsg.message)

            # Now we have message unpacked, lets iterate over every sample ...
            for s in l_vect.samples:

                # Every sample has two fields:
                # timestamp - system clock time of a moment of Sample`s creation
                # channels - a list of values - one for every channel
                LOGGER.debug("Got sample with timestamp: "+str(s.timestamp))

                # One can copy samples to numpy array ...
                a = numpy.array(s.channels)

                # Or just iterate over values ...
                for ch in s.channels:
                    LOGGER.debug(ch)

            # Having a new bunch of values one can fire some magic analysis and 
            # generate decision ....

            # Below we have quite simple decision-maker - it generates a random
            # decision every ~100 samples-bunch
            if random.random() > 0.99:
                # Here we send DECISION message somewhere-to-the-system ...
                # It's up to scenario's configuration how the decision will be used ...
                # Eg. it might be used by LOGIC module to push some button in speller.
                self.conn.send_message(message = str(random.randint(0,7)), 
                                       type = types.DECISION_MESSAGE, 
                                       flush=True)
        else:
            LOGGER.warning("Got unrecognised message type: "+str(mxmsg.type))

        # Tell the system 'I`ll not respond to this message, I`m just receiving'
        self.no_response()

if __name__ == "__main__":
    # Initialize and run an object in order to have your analysis up and running
    SampleAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
