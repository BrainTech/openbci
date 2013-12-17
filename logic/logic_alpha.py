
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import dbus
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings,variables_pb2


class LogicAlpha(ConfiguredMultiplexerServer):
    def __init__(self, addresses, type=peers.LOGIC_DECISION):
        super(LogicAlpha, self).__init__(addresses=addresses,
                                         type=type)
        session_bus = dbus.SessionBus()
        player = session_bus.get_object('org.mpris.clementine', '/Player')
        self.iface = dbus.Interface(player, dbus_interface='org.freedesktop.MediaPlayer')
        self.iface.VolumeSet(50)
        self.iface.Play()
        self.ready()

    def handle_message(self, mxmsg):
        if (mxmsg.type == types.DECISION_MESSAGE):
            l_decision = int(mxmsg.message)
            self.logger.info("Got decision: "+str(l_decision))
            self._run_post_actions(l_decision)
        else:
            pass

        self.no_response()

    def _run_post_actions(self, p_decision):
        vol = int(self.iface.VolumeGet())
        print '***********************{}*********************'.format(vol)
        if p_decision == 1 and vol != 100:
            print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            self.iface.VolumeSet(vol+10)
        elif p_decision == 0 and vol != 0:
            print 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
            self.iface.VolumeSet(vol-10)

if __name__ == "__main__":
    LogicAlpha(settings.MULTIPLEXER_ADDRESSES).loop()
    
