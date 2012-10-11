#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from multiplexer.multiplexer_constants import peers, types
from obci_utils import tags_helper
from obci_configs import variables_pb2

import Queue


from drivers import drivers_logging as logger
LOGGER = logger.get_logger("tags_to_mxmsg", "info")

class TagMsg(object):
    def get_message(self, tag, ts, mx=True):
        t = self._get_message(tag, ts)
        if mx:
            return types.TAG, tags_helper.pack_tag_from_tag(t)
        else:
            return types.TAG, t

    def _get_message(self, tag, ts):
        diff = tag['end_timestamp'] - tag['start_timestamp']
        tag['start_timestamp'] = ts
        tag['end_timestamp'] = ts + diff
        return tag

class BlinkMsg(object):
    def __init__(self, index_lambda=lambda t: int(t['desc']['blink'])):
        self.index_lambda = index_lambda

    def get_message(self, tag, ts, mx=True):
        if mx:
            return types.BLINK_MESSAGE, self._get_message(tag, ts).SerializeToString()
        else:
            return types.BLINK_MESSAGE, self._get_message(tag, ts)

    def _get_message(self, tag, ts):
        blink_msg = variables_pb2.Blink()
        blink_msg.timestamp = ts
        blink_msg.index = self.index_lambda(tag)
        return blink_msg

class DummyMsg(object):
    def get_message(self, tag, ts):
        return 1234, "dummy"



class TagsToMxmsg(object):
    def __init__(self, tags, handle_rules):
        """For every tag in tags find its corresponding
        handler"""
        self._eval_handle_rules(handle_rules)
        self.msgs = Queue.Queue()
        for t in tags:
            got_rule = False
            for rule, handler in self.handle_rules:
                if rule(t):
                    self.msgs.put((t, handler))
                    got_rule = True
                    break
            if not got_rule:
                LOGGER.warning("Tag does not fit to any rule: "+str(t))

    def _eval_handle_rules(self, handle_rules):
        """Evaluate and store tag handle rules used every time next_message is fired.
        handle_rules is a string in format '[(rule2, handler1), (rule2, handler2)...' so
        this is a list of pairs rule:handler

        - rule - determines whether tag applies to the handler, it shoult be 
        - - a lambda expression - meaning that rule is determined by a function
        - - other string - which by default means that rule is fulfielled when
            tag`s name is identical tu 'rule' string

        - handler - it is an instance class that handles tag - implements function fired like:
          get_message(tag, timestamp) that returns a pair: mxtype, mxmsg

        For instance rules-list:
        [('blink','BlinkMsg()'), 
         ('lambda t: t["dict"].has_key("blink_id")', 'BlinkMsg("lambda t: int(t[\"desc\"][\"blink_id\"]")'),
         ('tag','TagMsg()')]
        """
        self.handle_rules = []
        pairs = eval(handle_rules)
        for pair in pairs:
            rule_str, handler_str = pair
            if rule_str.startswith('lambda '): #assume it is lambda expression
                rule = eval(rule_str)
            else: #assume it is tag`s name
                rule = eval("lambda t: t['name'] == '"+rule_str+"'")
            handler = eval(handler_str)
            self.handle_rules.append((rule, handler))

    def next_message(self, ts, mx=True):
        try:
            tag, handler = self.msgs.get_nowait()
        except Queue.Empty:
            return None, None
        else:
            return handler.get_message(tag, ts, mx)

def run_test():
    """
    >>> tags = [{'name':'blink', 'desc':{'blink':1}}, {'name':'not-blink', 'desc':{'blink_id':2}}, {'name':'blink', 'desc':{'blink':11}}, {'name':'not-blink', 'desc':{'blink_id':22}}, {'name':'dupa', 'start_timestamp':1, 'end_timestamp':1.5, 'channels':'', 'desc': {}}]

    >>> rules = str([('blink', 'BlinkMsg()'), ('lambda t: t["desc"].has_key("blink_id")', 'BlinkMsg(lambda t: int(t["desc"]["blink_id"]))'), ('lambda t: True', 'TagMsg()')])

    >>> mgr = TagsToMxmsg(tags, rules)

    >>> mgr.next_message(10.0, False)[1].index
    1

    >>> mgr.next_message(20.0, False)[1].index
    2

    >>> mgr.next_message(30.0, False)[1].index
    11

    >>> mgr.next_message(40.0, False)[1].index
    22

    >>> mgr.next_message(50.0, False)[1]['end_timestamp'] #becouse gets new start_timestamp=50.0, has 0.5 len, so end_timestamp is 50.5
    50.5

    >>> mgr.next_message(40.0, False)[1]

    >>> rules = str([('lambda t: t["desc"].has_key("blink_id")', 'BlinkMsg(lambda t: int(t["desc"]["blink_id"]))')])

    >>> mgr = TagsToMxmsg(tags, rules)

    >>> mgr.next_message(10.0, False)[1].index
    2

    >>> mgr.next_message(20.0, False)[1].index
    22

    >>> mgr.next_message(30.0, False)[1]

    >>> 
    


    """
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("If no errors - tests SUCCEDED!!!")
