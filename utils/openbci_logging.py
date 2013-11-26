#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#     Joanna Tustanowska <joanna.tustanowska@titanis.pl>

"""Module defines a single method get_logger that returns logger with
set logging level. Change logging.INFO lines to change logging level."""
import os
import sys
import traceback
import logging
import logging.handlers

import decorator
import inspect


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


MAX_FILE_SIZE_B = 1000000
LOG_BUFFER_SIZE_B = 5000
BACKUP_COUNT = 2

USE_SENTRY = os.environ.get('SENTRY_DSN', False)

if USE_SENTRY == False:
    try:                                                                                          
        parser = SafeConfigParser()
        parser.read('/etc/default/openbci')
        send_logs = parser.get('sentry', 'send_logs')
        if send_logs == 'true':
            USE_SENTRY = parser.get('sentry', 'key')
            if USE_SENTRY == '':
                USE_SENTRY = False
    except:
        pass


try:
    from raven import Client
    from raven.handlers.logging import SentryHandler
    from raven.conf import setup_logging
except ImportError:
    print "raven-python modules not found, log messages will not be sent to Sentry"
    USE_SENTRY = False
    def _sentry_handler(sentry_key=None, obci_peer=None):
        return None
else:
    class OBCISentryClient(Client):

        def __init__(self, dsn=None, obci_peer=None, **options):
            super(OBCISentryClient, self).__init__(dsn, **options)
            self.peer = obci_peer

        def build_msg(self, event_type, data=None, date=None,
                  time_spent=None, extra=None, stack=None, public_key=None,
                  tags=None, **kwargs):
            data = super(OBCISentryClient, self).build_msg(event_type, data, date, time_spent,
                extra, stack, public_key, tags, **kwargs)

            tst = data.get('tags', None)
            if not tst:
                data['tags'] = {}
            if hasattr(self.peer, '_crash_extra_tags'):
                data['tags'].update(self.peer._crash_extra_tags())

            if hasattr(self.peer, '_crash_extra_data'):
                dt = data['extra'].get('data', {})
                up = self.peer._crash_extra_data()
                if dt:
                    data['extra']['data'].update(up)
                else:
                    data['extra']['data'] = up

            return data

    def _sentry_handler(sentry_key=None, obci_peer=None):
        try:
            client = OBCISentryClient(sentry_key, obci_peer=obci_peer, auto_log_stacks=True)
        except ValueError, e:
            print('logging setup: initializing sentry failed - ', e.args)
            return None
        handler = SentryHandler(client)
        handler.set_name('sentry_handler')
        setup_logging(handler)
        return handler


# print("logging setup: found raven and sentry key - %s" % USE_SENTRY)

def console_formatter():
    return logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def file_formatter():
    return logging.Formatter(
                    "%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s")

def mx_formatter():
    return logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")



def get_dummy_logger(p_name, p_level='info'):
    """Return logger with p_name as name. And logging level p_level.
    p_level should be in (starting with the most talkactive):
    'debug', 'info', 'warning', 'error', 'critical'."""
    logger = logging.getLogger(p_name)
    if len(logger.handlers) == 0:
        # Some module migh be imported few times. In every get_logger call
        # with p_name = "X" we return the same instance of logger, bu we must
        # ensure, that the logger has no more than one handler.
        handler = logging.StreamHandler()

        level = LEVELS[p_level]
        logger.setLevel(level)
        handler.setLevel(level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def get_logger(name, file_level='debug', stream_level='warning',
                            mx_level='warning', sentry_level='error',
                            conn=None, log_dir=None, obci_peer=None):
    """Return logger with name as name. And logging level p_level.
    p_level should be in (starting with the most talkactive):
    'debug', 'info', 'warning', 'error', 'critical'."""
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        # Some module migh be imported few times. In every get_logger call
        # with name = "X" we return the same instance of logger, bu we must
        # ensure, that the logger has no more than one handler.

        level = LEVELS['debug']
        logger.setLevel(level)
        formatter = console_formatter()

        shandler = logging.StreamHandler()
        shandler.setFormatter(formatter)
        stream_level = stream_level or 'warning'
        file_level = file_level or 'debug'
        mx_level = mx_level or 'warning'
        shandler.setLevel(LEVELS[stream_level])
        logger.addHandler(shandler)

        if conn is not None:
            import obci.utils.log_mx_handler as log_mx_handler
            mxhandler = log_mx_handler.LogMXHandler(conn)
            mxhandler.setLevel(LEVELS[mx_level])
            mxhandler.setFormatter(mx_formatter())
            logger.addHandler(mxhandler)


        if log_dir is not None:
            log_dir = os.path.expanduser(log_dir)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            fhandler = logging.handlers.RotatingFileHandler(
                                    os.path.join(log_dir, name + ".log"),
                                    maxBytes=MAX_FILE_SIZE_B,
                                    backupCount=BACKUP_COUNT)
            fhandler.setFormatter(formatter)
            fhandler.setLevel(LEVELS[file_level])
            fhandler.setFormatter(file_formatter())
            # memhandler = logging.handlers.MemoryHandler(LOG_BUFFER_SIZE_B,
            #                                     flushLevel=LEVELS['warning'],
            #                                            target=fhandler)
            # memhandler.setLevel(LEVELS file_level])
            logger.addHandler(fhandler)
        if USE_SENTRY:
            h = _sentry_handler(obci_peer=obci_peer)
            if h:
                h.setLevel(LEVELS[sentry_level])
                logger.addHandler(h)

    return logger


@decorator.decorator
def log_crash(meth, *args, **kwargs):
    try:
        return meth(*args, **kwargs)
    except Exception, e:
        self = args[0]
        # print "self:   ", self
        if hasattr(self, 'logger'):
            info = sys.exc_info()
            frames = inspect.getouterframes(info[2].tb_frame)
            extra_obj = _find_extra_obj(frames)

            msg = crash_log_msg(meth, args, kwargs, extra_obj, info, e)
            extra = { 'data' : {}, 'tags' : {}}
            extra['data'].update(crash_log_data(e, extra_obj))
            extra['tags'].update(crash_log_tags(e, extra_obj))
            extra['culprit'] = caller_name(skip=2)
            self.logger.critical(msg, exc_info=True, extra=extra)
            del info
            del frames

        raise(e)


def _find_extra_obj(frames):
    for frame in frames:
        arg_info = inspect.getargvalues(frame[0])
        if len(arg_info.args) > 0 and arg_info.args[0] == 'self':
            callee = arg_info.locals['self']
            if hasattr(callee, '_crash_extra_tags'):
                return callee
    return None



def crash_log_tags(exception, callee):
    if hasattr(callee, '_crash_extra_tags'):
        return callee._crash_extra_tags(exception)
    else:
        return {}

def crash_log_msg(func, args, kwargs, callee=None, exc_info=None, exception=None):
    msg = ' \n\n  CRASH INFO:\n'
    if exception:
        msg += "Peer crashed with exception %s\n" % str(exception)
    if exc_info:
        fmt = traceback.format_exception(exc_info[0], exc_info[1], exc_info[2])
        fmt_str = ''.join(fmt)
        msg += fmt_str

    msg += "\nfunction/method  %s called with  args: %s" % (func, args)
    msg += "\n\nkwargs:  %s" % kwargs

    if hasattr(callee, '_crash_extra_description'):
        msg += "\n\n" + callee._crash_extra_description(exception)
    del exc_info
    return msg

def crash_log_data(exception, callee):
    if hasattr(callee, '_crash_extra_data'):
        return callee._crash_extra_data(exception)
    else:
        return {}


def caller_name(skip=2):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
       copied from gist:  https://gist.github.com/techtonik/2151727
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append( codename ) # function or a method
    del parentframe
    return ".".join(name)



