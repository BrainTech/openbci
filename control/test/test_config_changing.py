#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2

from multiplexer.clients import connect_client
import obci.control.common.config_message as cmsg

class SomethingThatChangesConfigs(object):

    def run(self):
        conn = connect_client(type=peers.CONFIGURER, addresses=settings.MULTIPLEXER_ADDRESSES)
        time.sleep(4)
        for i in range(5):
            msg = cmsg.fill_msg(types.UPDATE_PARAMS, sender="p_a")
            params = dict(p=str(i))
            cmsg.dict2params(params, msg)
            try:
                conn.send_message(message=msg, type=types.UPDATE_PARAMS)
                resp, sth = conn.receive_message()
                msg = cmsg.unpack_msg(resp.type, resp.message)
                print "got   ", msg
            except Exception as e:
                print "error: ", e.args, "  ", type(e)
            print i


if __name__ == "__main__":
    something = SomethingThatChangesConfigs()
    time.sleep(1)
    something.run()
