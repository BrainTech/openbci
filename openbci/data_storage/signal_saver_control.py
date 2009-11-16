#!/usr/bin/env python

import math
import time
import sys
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


class SignalSaverControl(object):
    def __init__(self):
        self._connection = connect_client(type = peers.SIGNAL_SAVER_CONTROL)
    def run(self):
        l_input = ""
        l_msg_type = types.SIGNAL_SAVER_CONTROL_MESSAGE
        while True:
            print("Type: finish_saving and hit enter to stop signal_saver...")
            l_input = raw_input()
            if l_input == 'finish_saving':
                self._connection.send_message(message=l_input, type=l_msg_type, flush=True)
            else:
                print("Unrecognised input: "+l_input)
                print("Try again:)")

if __name__ == "__main__":
   SignalSaverControl().run()

