#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import urllib


class TestRobot(object):
    def __init__(self, robot_ip):
        self.robot_ip = robot_ip

    def head_up(self):
        # http://192.168.10.18/rev.cgi?Cmd=nav&action=18&drive=13&speed=5
        params = urllib.urlencode({'Cmd': 'nav',
                                    'action': 18,
                                    'drive': 13,
                                    'speed' : 5})
        print params
        try:
            # f = urllib.urlopen("http://" + self.robot_ip + "/rev.cgi?%s" % params)
            f = urllib.urlopen("http://192.168.1.9/rev.cgi?Cmd=nav&action=1")
        except IOError, e:
            print "Connection error: ", str(e)
        else:
            print f.read()

def parser():
    parser = argparse.ArgumentParser(description="Test ROVIO robot!", epilog="(c) 2011, Warsaw University")
    parser.add_argument('robot_ip', help='IP address of the ROVIO robot.')
    return parser

if __name__ == '__main__':
    args = parser().parse_args()

    robot = TestRobot(args.robot_ip)
    robot.head_up()
