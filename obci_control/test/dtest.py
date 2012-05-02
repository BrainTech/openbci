#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import wraps

class HandlerCollection(object):
    def __init__(self):
        self.handlers = {}
        self.default = self._default_handler
        self.error = self._error_handler

    def new_from(other):
        new = HandlerCollection()
        new.handlers = dict(other.handlers)
        new.default = other.default
        new.error = other.error
        return new


    def _default_handler(*args):
        pass

    def _error_handler(*args):
        pass

    def handler(self, message_type):
        def save_handler(fun):
            self.handlers[message_type] = fun
            return fun
        return save_handler

    def default_handler(self):
        def save_default_handler(fun):
            self.default = fun
            return fun
        return save_default_handler

    def error_handler(self):
        def save_error_handler(fun):
            self.error = fun
            return fun
        return save_error_handler

    def handler_for(self, message_name):
        handler = self.handlers.get(message_name, None)

        return handler


class DTest(object):
    msg_handlers = HandlerCollection()

    def handle_something(self, key):
        method = self.msg_handlers.handler_for(key)

        if method is None:
            print "error: unknown key", key
        else:
            print "calling method", method.__name__
            method(self, "123456789")


    @msg_handlers.handler("dupa")
    def dupa_handler(self, arg):
        print self
        print "I am a dupa handler", arg

    @msg_handlers.handler("ble")
    def another_handler(self, arg):
        print self
        print "tralala", arg

    @msg_handlers.default_handler()
    def default_handler(self, arg):
        print "default handler --------"


class D(DTest):
    msg_handlers = super.msg_handlers.new_from(DTest.msg_handlers)

    @msg_handlers.handler("ble")
    def assasd(self, arg):
        """changed"""
        print "changed"

    @msg_handlers.handler("dupa")
    def dupa_handler(self, arg):
        """Subclassed"""
        print "subcl"

class A(DTest):
    msg_handlers = HandlerCollection.new_from(DTest.msg_handlers)

    @DTest.msg_handlers.handler("ble")
    def assd(self, arg):
        """AAA changed"""
        print "----"

    @DTest.msg_handlers.handler("dupa")
    def dupa_handler(self, arg):
        """AAAA Subclassed"""
        print "AAAA subcl"

print "subclass", D.msg_handlers

if __name__ == '__main__':
    dt = D()
    aa = A()

    dt.handle_something("dupa")
    dt.handle_something("ble")
    dt.handle_something("oaoao")