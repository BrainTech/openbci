#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Joanna Tustanowska <jnn@jnnt.net>

import urllib2
import urllib

import argparse
import cookielib

import signal
import sys

import time
import threading

class TahoeHTTP(object):
    def __init__(self, tahoe_ip, user, password):

        self.tahoe_ip = tahoe_ip
        self.base_uri = 'http://' + self.tahoe_ip
        self.user = user
        self.passwd = password

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, self.base_uri, self.user, self.passwd)
        auth_handler = urllib2.HTTPBasicAuthHandler(passman)
        cj = cookielib.CookieJar()

        opener = urllib2.build_opener(auth_handler, urllib2.HTTPCookieProcessor(cj))
        opener.addheaders.append(('User-agent', 'Mozilla/4.0'))
        opener.addheaders.append(('Referer', self.base_uri))
        urllib2.install_opener(opener)
        self.opn = opener
        print "----"
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())

    def signal_handler(self):
        def handler(signum, frame):
            print "Signal intercepted! ", signum
            sys.exit(-signum)
        return handler

    def action(self, outlet_no, action):
        url = self.base_uri + '/_power?a=' +action +'&amp;u=1&amp;p=' + str(outlet_no)
        print url
        data = {'login':self.user,
                'pass' : self.passwd}
        post = urllib.urlencode(data)

        print "*****"
        try:
            res = self.opn.open(url, post, timeout=9)
        except Exception, e:
            print "Exception: ", str(e)
            return 1
        print "juszsz"
        return 0
        # print res.info()
        # print res.read()

    def power_on(self, outlet_no):
        print "OOOONNNN"
        self.action(outlet_no, 'on')

    def power_off(self, outlet_no):
        print "OOOOFFFFF"
        self.action(outlet_no, 'off')


def arg_parser():
    parser = argparse.ArgumentParser(description="Send commands ON/OFF to outlets on the Tahoe device")
    parser.add_argument('command', help="command on/off", choices=['on', 'off'])
    parser.add_argument('outlet_no', help="Outlet number", choices='1234')
    parser.add_argument('--ip', help="IP address of the Tahoe.", default='192.168.1.53')
    parser.add_argument('--user', help='User name', default='root')
    parser.add_argument('--passwd', help='Password', default='Tahoe')
    return parser

if __name__ == '__main__':
    args = arg_parser().parse_args()
    taho = TahoeHTTP(args.ip, args.user, args.passwd)
    result = taho.action(args.outlet_no, args.command)
    sys.exit(result)