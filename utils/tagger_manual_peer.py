#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@titanis.pl>
#
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import variables_pb2, settings

from obci.utils import tags_helper
from obci.utils.tag_gui import TagGui
from PyQt4 import QtGui, QtCore

import sys
import time

class TaggerManual(ConfiguredClient):
    def __init__(self, addresses):
        super(TaggerManual, self).__init__(addresses=addresses,
                                     type=peers.TAGS_SENDER)
        self.app = QtGui.QApplication(sys.argv)
        self.gui = TagGui(self.config.get_param('tag_names').split(';'))
        self.gui.tag.connect(self.send_tag)
        self.ready()

    def run(self):
        self.app.exec_()
        
    def send_tag(self, name):
        t = time.time()
        tags_helper.send_tag(self.conn, t, t, str(name), p_tag_desc={}, p_tag_channels="")


if __name__ == '__main__':
    TaggerManual(settings.MULTIPLEXER_ADDRESSES).run()

