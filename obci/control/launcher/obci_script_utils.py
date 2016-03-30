#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import errno
import socket
import subprocess

import obci.control.common.net_tools as net
import obci.control.common.obci_control_settings as settings
import obci.control.launcher.obci_client as obci_client
import obci.control.launcher.view as view


disp = view.OBCIViewText()


def launch_obci_server(args=[]):
    #path = obci_server.__file__
    #path = '.'.join([path.rsplit('.', 1)[0], 'py'])
    
    # FIXME
    path = '~/openbci/bin/obci_server'
    
    try:
        #if '--win-silent' in args:
        #    python_command = 'pythonw'
        #    args.remove('--win-silent')
        #else:
        #    python_command = 'python'
        #srv = subprocess.Popen([python_command, path] + list(args))
        srv = subprocess.Popen([path] + list(args))
    except Exception, e:
        print 'Server launch error:', str(e)
        return None
    return srv

def argv():
    return sys.argv[2:]

def server_process_running(expected_dead=False):
    """
    Return true if there is an obci_server process running
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    running = False

    for i in range(5):
        try:
            sock.connect((socket.gethostname(), int(net.server_rep_port())))
        except socket.error, e:
            if e.errno == errno.ECONNREFUSED:
                running = False
                if expected_dead:
                    break
            elif e.errno == errno.EISCONN:
                running = True
                break
            else:
                print str(e)
        else:
            running = True
            break

        time.sleep(0.3)

    sock.close()
    return running

def client_server_prep(cmdargs=None, client_class=obci_client.OBCIClient, server_ip=None, start_srv=True, zmq_ctx=None):

    directory = os.path.abspath(settings.DEFAULT_SANDBOX_DIR)
    if not os.path.exists(directory):
        print "obci directory not found: {0}".format(directory)
        raise OBCISystemError()

    client = None
    srv = None

    os.chdir(directory)

    srv_rep_port = net.server_rep_port()
    srv_pub_port = net.server_pub_port()
    if server_ip:
        rep_addrs = ['tcp://'+server_ip+':'+srv_rep_port]
        pub_addrs = ['tcp://'+server_ip+':'+srv_pub_port]
    else:
        rep_addrs = ['tcp://*:' + srv_rep_port]
        pub_addrs = ['tcp://*:' + srv_pub_port]

    if not server_process_running() and not start_srv:
        disp.view("Start obci_server (command: obci srv) before performing other tasks")
        return None

    if not server_process_running() and\
            (not server_ip or server_ip == net.lo_ip())\
            and start_srv:
        print "will launch server"
        args = argv() if cmdargs else []
        if rep_addrs and pub_addrs:
            args += ['--rep-addresses'] + rep_addrs + ['--pub-addresses'] + pub_addrs
        srv = launch_obci_server(args)
        if not srv:
            disp.view("Could not launch OBCI Server")
            return None
        disp.view("OBCI server launched. PID: {0}".format(srv.pid))


    if not server_ip:
        rep_addrs = ['tcp://localhost:'+srv_rep_port]

    res, client = connect_client(rep_addrs, client_class=client_class, zmq_ctx=zmq_ctx)

    if res is None:
        disp.view("Could not connect to OBCI Server")
        client = None

    return client
