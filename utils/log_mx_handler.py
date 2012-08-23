#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module defines logging handler class for Multiplexer peers,
a LogMXHandler.
"""

import logging
import json

from multiplexer.multiplexer_constants import types

class LogMXHandler(logging.Handler):
    """
The handler pickles log records and sends them
to the multiplexer as OBCI_LOG_MESSAGE. The records should be
picked up by a log collector mx peer."""

    def __init__(self, conn):
        # store multiplexer connection object
        self.conn = conn
        # super(LogMXHandler, self).__init__()
        logging.Handler.__init__(self)

    def close(self):
        pass
        # self.conn.close()

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it for pickling first.
        """
        # print "  ## ## ## ## ## ##  emit!!! ", record
        try:
            # The format operation gets traceback text into record.exc_text
            # (if there's exception data), and also puts the message into
            # record.message. We can then use this to replace the original
            # msg + args, as these might be unpickleable. We also zap the
            # exc_info attribute, as it's no longer needed and, if not None,
            # will typically not be pickleable.
            self.format(record)
            record.msg = record.message
            record.args = None
            record.exc_info = None
            # print record.__dict__
            data = json.dumps(record.__dict__)
            self.conn.send_message(
                        message=data, type=types.OBCI_LOG_MESSAGE, flush=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
