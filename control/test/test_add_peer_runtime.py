#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
import time
import launcher.obci_script as obci_script


ctx = zmq.Context()
client = obci_script.client_server_prep(server_ip='127.0.0.1',
                                                    zmq_ctx=ctx,
                                                    start_srv=False)

# res = client.launch(launch_file='scenarios/amplifier/dummy_full_cap.ini', name='AAAA TEST')


# print res

res = client.add_peer('A', 'testowy_peer', 'control/test/peer_b.py', machine='traktor')
# res = client.add_peer('A', 'testowy_peer', 'control/test/peer_b.py', machine='mati-laptop')

print res


time.sleep(3)

res = client.kill_peer('A', 'testowy_peer', remove_config=True)

print res
