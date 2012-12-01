#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.clients import connect_client

from obci.control.peer.peer_control import PeerControl, ConfigNotReadyError
import common.config_message as cmsg
from obci.utils.openbci_logging import get_logger
import sys


class ConfiguredClient(object):

    def __init__(self, addresses, type, external_config_file=None):

        self.conn = connect_client(addresses=addresses, type=type)
        self.ready_to_work = False
        self.external_config_file = external_config_file
        self.config = PeerControl(peer=self)

        self.logger = get_logger(self.config.peer_id,
                            file_level=self.get_param('file_log_level'),
                            stream_level=self.get_param('console_log_level'),
                            mx_level=self.get_param('mx_log_level'),
                            conn=self.conn,
                            log_dir=self.get_param('log_dir'))
        self.config.logger = self.logger

        self.config.connection = self.conn
        self.config.peer_validate_params = self.validate_params
        self.config.peer_params_change = self.params_changed
        result, details = self.config.initialize_config(self.conn)


        if not result:
            self.logger.critical(
                        'Config initialisation FAILED: {0}'.format(details))
            sys.exit(1)
        else:
            self.validate_params(self.config.param_values())

    def get_param(self, param_name):
        return self.config.get_param(param_name)

    def set_param(self, param_name, param_value):
        self.config.set_param(param_name, param_value)

    def ready(self):
        self.ready_to_work = True
        self.config.register_config(self.conn)
        self.config.send_peer_ready(self.conn)


    def validate_params(self, params):
        self.logger.info("VALIDATE PARAMS, {0}".format(params))
        return True

    def params_changed(self, params):
        self.logger.info("PARAMS CHAnGED, {0}".format(params))
        return True
