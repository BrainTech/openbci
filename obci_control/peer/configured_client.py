#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.clients import connect_client

from peer.peer_control import PeerControl, ConfigNotReadyError
import common.config_message as cmsg

class ConfiguredClient(object):

    def __init__(self, type, addresses, connect_config=True):
        self.config = PeerControl(self,
                                    param_validate_method=self.validate_params,
                                    param_change_method=self.params_changed)
        self.conn = connect_client(type, addresses)

        if not self.init_config(connect_config):
            raise ConfigNotReadyError(str(self.config))

    def init_config(self, connect_config):
        if connect_config:
            return self.config.initialize_config(self.conn)
        else:
            return self.config.initialize_config_locally()

    def send_peer_ready(self):
        self.ready_to_work = True
        self.config.send_peer_ready(self.conn)

    def validate_params(self, params):
        print '[',self.config.peer_id,"] VALIDATE PARAMS, {0}".format(params)
        return True

    def params_changed(self, params):
        print '[',self.config.peer_id,"] PARAMS CHAnGED, {0}".format(params)
        return True