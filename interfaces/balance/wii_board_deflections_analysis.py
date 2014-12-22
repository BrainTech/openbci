#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from obci.configs import settings

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class WiiBoardDeflectionsAnalysis(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses, p_type = peers.WII_BOARD_SIGNAL_CATCHER):#todo - update peer type):
        super(WiiBoardDeflectionsAnalysis, self).__init__(addresses=addresses, type=p_type)
        # set maxes - left, right, up, down: either -1 1 (if used in scenario for calibration) or user-s max deflections from calibration
        # set stanie swobodne area
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_SIGNAL_MESSAGE:
            v = variables_pb2.SampleVector()
            v.ParseFromString(mxmsg.message)
            for s in v.samples:#todo - refactor in regard to utils/wii_2d_router
                msg = variables_pb2.Sample2D()
                sum_mass = sum(s.channels[0:4])
                x = (((s.channels[1] + s.channels[2]) - (s.channels[0] + s.channels[3]))/sum_mass) + 0.5
                y = (((s.channels[1] + s.channels[0]) - (s.channels[2] + s.channels[3]))/sum_mass) + 0.5
                #apply filtering somwere here
                sway_direction, sway_level = self._calculate_sway(x, y)
                msg.x = sway_direction
                msg.y = sway_level
                msg.timestamp = time.time()
                self.conn.send_message(message=msg.SerializeToString(),
                                       type=types.ETR_SIGNAL_MESSAGE, flush=True)#todo - update sent format
        else:
            pass #todo - log warning
        self.no_response()
    def _calculate_sway(self, x, y):
        #using self.maxes and self.stanie swobodne area
        #calculate sway direction and sway level 
        return 0, 50

if __name__ == "__main__":
    WiiBoardDeflectionsAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
