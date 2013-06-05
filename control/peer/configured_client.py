#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.clients import connect_client

from obci.control.peer.peer_control import PeerControl, ConfigNotReadyError
import obci.control.common.config_message as cmsg
from obci.utils.openbci_logging import get_logger, log_crash
import sys

class ConfiguredClient(object):

    @log_crash
    def __init__(self, addresses, type, external_config_file=None):

        self.conn = connect_client(addresses=addresses, type=type)
        self.ready_to_work = False
        self.external_config_file = external_config_file
        self.config = PeerControl(peer=self)

        self.logger = get_logger(self.config.peer_id,
                            file_level=self.get_param('file_log_level'),
                            stream_level=self.get_param('console_log_level'),
                            mx_level=self.get_param('mx_log_level'),
                            sentry_level=self.get_param('sentry_log_level'),
                            conn=self.conn,
                            log_dir=self.get_param('log_dir'),
                            obci_peer=self)
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

    @log_crash
    def get_param(self, param_name):
        return self.config.get_param(param_name)

    @log_crash
    def set_param(self, param_name, param_value):
        self.config.set_param(param_name, param_value)

    @log_crash
    def ready(self):
        self.ready_to_work = True
        self.config.register_config(self.conn)
        self.config.send_peer_ready(self.conn)

    def validate_params(self, params):
        self.logger.info("VALIDATE PARAMS, {0}".format(params))
        return True

    @log_crash
    def params_changed(self, params):
        self.logger.info("PARAMS CHAnGED, {0}".format(params))
        return True

    def _param_vals(self):
        vals = self.config.param_values()
        if 'channels_info' in vals:
            vals['channels_info'] = '[...truncated...]'
        return vals

    def _crash_extra_description(self, exc=None):
        return "peer %s config params: %s" % (self.config.peer_id,
                                                self._param_vals())

    def _crash_extra_data(self, exc=None):
        """This method is called when the peer crashes, to provide additional
        peer data to the crash report.
        Should return a dictionary."""

        return {
            "config_params" : self._param_vals(),
            "peer_id": self.config.peer_id,
            "experiment_uuid": self.get_param("experiment_uuid")
        }

    def _crash_extra_tags(self, exception=None):
        return {'obci_part' : 'obci',
                "experiment_uuid": self.get_param("experiment_uuid")}