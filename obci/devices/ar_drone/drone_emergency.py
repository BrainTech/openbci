#!/usr/bin/env python

import libardrone

ip = '192.168.1.19'
drone = libardrone.ARDrone(ip)
drone.land()

