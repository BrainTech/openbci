#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import variables_pb2, settings

from obci.utils import tags_helper
from obci.utils.tagger_gui.tagger_manual_gui import TagGui
from PyQt4 import QtGui, QtCore

import sys
import time

class TaggerManual(ConfiguredClient):
    def __init__(self, addresses):
        super(TaggerManual, self).__init__(addresses=addresses,
                                     type=peers.TAGS_SENDER)
        self.app = QtGui.QApplication(sys.argv)
        self.gui = TagGui()
        self.gui.tag_signal.connect(self.send_tag)
        self._menage_params()
        self.gui.initUI(self.frames_params, self.display_list)

        self.ready()

    def _menage_params(self):
        self.display_list = self.get_param('display_list').split(';')
        tags = self.get_param('tags').split(';')
        timers = self.get_param('timers').split(';')
        self.frames_params = []
        for frame in self.display_list:
            params = self.get_param(frame)
            if frame in timers:
                self.frames_params.append(('timer', frame, eval(params)))
                timers.remove(frame)
            elif frame in tags:
                self.frames_params.append(('tag', frame, eval(params)))
                tags.remove(frame)

    def run(self):
        self.app.exec_()
        
    def send_tag(self, tag):
        tag = eval(str(tag)) 
        tags_helper.send_tag(self.conn, float(tag['timestamp']), float(tag['timestamp']), tag['name'], p_tag_desc={}, p_tag_channels="")


if __name__ == '__main__':
    TaggerManual(settings.MULTIPLEXER_ADDRESSES).run()

