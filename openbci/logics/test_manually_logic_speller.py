#!/usr/bin/env python
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

class ManualSpellerLogicControl(object):
    def __init__(self):
        self._connection = connect_client(type = peers.ANALYSIS)
    def run(self):
        l_input = ""
        l_msg_type = types.DECISION_MESSAGE
        print("IF YOU DIDN`T FIRE UGM AND SPELLER LOGIC BEFORE RUNNING THIS SCRIPT DO IT NOW!!!")
        while True:
            print("Type decision message to be sent to logic (a number from 0-7)")
            l_input = raw_input()
            # Decision made, send the decision to logics
            decision = int(l_input)
            dec = variables_pb2.Decision()
            dec.decision = decision
            dec.type = 0
            self._connection.send_message(message = dec.SerializeToString(), type = l_msg_type, flush=True)
if __name__ == "__main__":
    ManualSpellerLogicControl().run()

