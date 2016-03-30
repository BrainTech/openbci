#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import settings, variables_pb2, configurer
import os, time
SLEEP_TIME = 0.1
def run():
    configs = configurer.Configurer(settings.MULTIPLEXER_ADDRESSES).get_configs(['SPELLER_TEXT_ID', 'PEER_READY'+str(peers.UGM)])
    msg = {'id': int(configs['SPELLER_TEXT_ID']),
               'message': ""
               }

    msgs = []
    msgs.append( msg)

    conn = connect_client(type = peers.ETR_AMPLIFIER)
    l_ugm_msg = variables_pb2.UgmUpdate()
    l_ugm_msg.type = 1
    l_ugm_msg.value = ""

    
    prev = os.popen('xsel -b').read()
    while True:
        s = os.popen('xsel -b').read()
        if s != prev:
            print(s)
            msg['message'] = s.decode('utf-8')
            l_ugm_msg.value = str(msgs)
            conn.send_message(
                message = l_ugm_msg.SerializeToString(), 
                type=types.UGM_UPDATE_MESSAGE, flush=True)
            prev = s
        time.sleep(SLEEP_TIME)
if __name__ == '__main__':
    run()
