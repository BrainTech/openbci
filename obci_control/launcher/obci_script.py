#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import argparse
import json
import time
import subprocess
import sys
import ConfigParser
import signal
import errno
import socket

import zmq

import launcher_tools
launcher_tools.update_obci_syspath()
launcher_tools.update_pythonpath()

import obci_server
import obci_client
import common.obci_control_settings as settings
import common.net_tools as net
import view
from common.config_helpers import OBCISystemError
from peer.peer_cmd import PeerCmd
import peer.peer_cmd as peer_cmd


disp = view.OBCIViewText()

def cmd_srv(args):
    client_server_prep(args)

def cmd_srv_kill(args):
    running = server_process_running(expected_dead=True)
    if not running:
        disp.view("Server was not running...")
        return

    client = client_server_prep()
    if not client:
        print "srv_kill unsuccessful (client creation error)"
        sys.exit(1)
    client.srv_kill()

    if server_process_running(expected_dead=True):
        disp.view('obci server kill signal unsuccesful, try killing the process')
    else:
        disp.view("Server process terminated.")


def cmd_launch(args):
    launch_f = os.path.abspath(args.launch_file)
    overwrites = args.ovr
    if overwrites:
        pack = peer_cmd.peer_overwrites_pack(overwrites)
        print pack
    else:
        pack = None
    
    client = client_server_prep()
    if not client:
        sys.exit(1)

    response = client.launch(launch_f, args.sandbox_dir, args.name, pack)
    disp.view(response)


def cmd_morph(args):

    launch_f = os.path.abspath(args.launch_file)
    overwrites = args.ovr
    if overwrites:
        pack = peer_cmd.peer_overwrites_pack(overwrites)
        print pack
    else:
        pack = None
    
    client = client_server_prep()
    if not client:
        sys.exit(1)
    print args.leave_on
    response = client.morph(args.experiment, launch_f, args.name, pack, args.leave_on)
    disp.view(response)


def cmd_new(args):
    if args.launch_file:
        launch_f = os.path.abspath(args.launch_file)
    else:
        launch_f = ''
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.send_create_experiment(launch_f, args.sandbox_dir, args.name)
    disp.view(response)

def cmd_start(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.start_chosen_experiment(args.experiment)
    disp.view(response)

def cmd_join(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.join_experiment(args.id, args.peer_id, args.peer_path)
    if response.type == 'rq_ok':
        pass
    disp.view(response)

def cmd_kill(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    response = client.kill_exp(args.id)
    disp.view(response)

def cmd_killall(args):
    pass

def cmd_add(args):
    pass

def cmd_save(args):
    pass

def cmd_log(args):
    pass

def cmd_config(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    ovr = dict(local_params=args.local_params,
            external_params=args.external_params,
            launch_dependencies=args.launch_dependencies,
            config_sources=args.config_sources)

    response = client.configure_peer(args.experiment, args.peer_id, ovr,
                            args.config_file)
    disp.view(response)


def cmd_info(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    if not args.e:
        response = client.send_list_experiments()
    else:
        response = client.get_experiment_details(args.e, args.p)
    if response is None:
        response = "whyyyy"
    disp.view(response)

def cmd_tail(args):
    client = client_server_prep()
    if not client:
        sys.exit(1)
    if not args.e:
        response = client.send_list_experiments()
    elif not args.p:
        response = client.get_experiment_details(args.e, args.p)
    else:
        response = client.get_tail(args.e, args.p, args.l)
    if response is None:
        response = "whyyyy"
    disp.view(response)


########################################################


###############################################################################



def obci_arg_parser():
    parser = argparse.ArgumentParser(description="Launch and manage OBCI experiments,\
their state and configuration", epilog="(c) 2011, Warsaw University", prog='obci')
    configure_argparser(parser)
    return parser

def configure_argparser(parser):
    subparsers = parser.add_subparsers(title='available commands',
    description='(use %(prog)s *command* -h for help on a specific command)',
    dest='command_name')

    conf_parser = PeerCmd().conf_parser
#------------------------------------------------------------------------------
    parser_srv = subparsers.add_parser('srv',
                parents=[obci_server.server_arg_parser(add_help=False)],
                help="Start OBCIServer")

    parser_srv.set_defaults(func=cmd_srv)
#------------------------------------------------------------------------------
    parser_srv_kill = subparsers.add_parser('srv_kill',
                parents=[obci_server.server_arg_parser(add_help=False)],
                help="Kill OBCIServer")
    parser_srv_kill.set_defaults(func=cmd_srv_kill)
#------------------------------------------------------------------------------
    parser_launch = subparsers.add_parser('launch',
                help="Launch an OpenBCI system with configuration \
specified in a launch file or in a newly created Experiment")

    parser_launch.add_argument('launch_file', type=path_to_file,
                help="OpenBCI launch configuration (experiment configuration).")
    parser_launch.add_argument('--sandbox_dir', type=path_to_file,
                help="Directory for log file and various temp files storeage.")
    parser_launch.add_argument('--name',
                help="A name for experiment")
    parser_launch.add_argument('--ovr', nargs=argparse.REMAINDER)#, type=peer_args)
    parser_launch.set_defaults(func=cmd_launch)
#------------------------------------------------------------------------------
    parser_morph = subparsers.add_parser('morph',
                help='Transform chosen scenario into another, optionally not restarting \
some peers')
    parser_morph.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_morph.add_argument('launch_file', type=path_to_file,
                help="OpenBCI launch configuration (experiment configuration).")
    parser_morph.add_argument('--name',
                help="A name for experiment")
    parser_morph.add_argument('--leave_on', nargs='*',# action='append',
                help="A name for experiment")
    parser_morph.add_argument('--ovr', nargs=argparse.REMAINDER)
    parser_morph.set_defaults(func=cmd_morph)
#------------------------------------------------------------------------------
    parser_add = subparsers.add_parser('add',
                help="Add a peer to an experiment launch configuration")
#------------------------------------------------------------------------------
    parser_new = subparsers.add_parser('new',
                help="Create a new experiment launch configuration")
    parser_new.add_argument('--launch_file', type=path_to_file,
                help="OpenBCI launch configuration (experiment configuration).")
    parser_new.add_argument('--sandbox_dir', type=path_to_file,
                help="Directory for log file and various temp files storeage.")
    parser_new.add_argument('--name',
                help="A name for experiment")
    parser_new.set_defaults(func=cmd_new)
#------------------------------------------------------------------------------
    parser_kill = subparsers.add_parser('kill',
                help="Kill an OpenBCI experiment")
    parser_kill.add_argument('id', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_kill.add_argument('--brutal', help='Just kill the specified experiment manager, \
do not send a "kill" message')
    parser_kill.set_defaults(func=cmd_kill)
#------------------------------------------------------------------------------
    parser_killall = subparsers.add_parser('killall',
                help="Kill everything: all experiments and OBCI server.")
#------------------------------------------------------------------------------
    parser_join = subparsers.add_parser('join', parents=[conf_parser],
                help="Join a running OpenBCI experiment with a new peer.")
    parser_join.add_argument('id', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_join.add_argument('peer_id',
                                    help="Unique name for this peer")
    parser_join.add_argument('peer_path', type=path_to_file,
                help="Path to an executable file.")

    parser_join.set_defaults(func=cmd_join)
#------------------------------------------------------------------------------

    parser_config = subparsers.add_parser('config',
                help="Change a single peer configuration", parents=[conf_parser])
    parser_config.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_config.add_argument('peer_id', help='Peer ID in the specified experiment.')
    parser_config.set_defaults(func=cmd_config)
#------------------------------------------------------------------------------
    parser_save = subparsers.add_parser('save',
                help="Save OBCI experiment configuration to a launch file or save\
                        a peer configuration")
#------------------------------------------------------------------------------
    parser_start = subparsers.add_parser('start',
                help='Send start command to a chosen experiment.')
    parser_start.add_argument('experiment', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_start.set_defaults(func=cmd_start)
#------------------------------------------------------------------------------
    parser_info = subparsers.add_parser('info',
                help="Get information about controlled OpenBCI experiments\
                        and peers")
    parser_info.add_argument('-e', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_info.add_argument('-p', help='Peer ID in the specified experiment.')
    parser_info.set_defaults(func=cmd_info)
#------------------------------------------------------------------------------
    parser_tail = subparsers.add_parser('tail',
                help="View output tail of a chosen peer.")
    parser_tail.add_argument('-e', help='Something that identifies experiment: \
a few first letters of its UUID or of its name \
(usually derived form launch file name)')
    parser_tail.add_argument('-p', help='Peer ID in the specified experiment.')
    parser_tail.add_argument('-l', help='Number of lines to get')
    parser_tail.set_defaults(func=cmd_tail)
#------------------------------------------------------------------------------

###############################################################################

###############################################################################

def connect_client(addresses, client=None, client_class=obci_client.OBCIClient):
    if client is None:
        ctx = zmq.Context()
        try:
            client = client_class(addresses, ctx)
        except Exception, e:
            print "client creation error: ", str(e)
            return None, None
    result = client.ping_server(timeout=9000)

    return result, client



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


def client_server_prep(cmdargs=None, client_class=obci_client.OBCIClient, server_ip=None):

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

    if not server_process_running() and not server_ip:
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

    res, client = connect_client(rep_addrs, client_class=client_class)
    
    if res is None:
        disp.view("Could not connect to OBCI Server")
        client = None

    return client


def launch_obci_server(args=[]):
    path = obci_server.__file__
    path = '.'.join([path.rsplit('.', 1)[0], 'py'])
    try:
        srv = subprocess.Popen(['python', path] + list(args))
    except Exception, e:
        print 'Server launch error:', str(e)
        return None
    return srv

def path_to_file(string):
    if not os.path.exists(string):
        msg = "{0} -- path not found!".format(string)
        raise argparse.ArgumentTypeError(msg)
    return string

def argv():
    return sys.argv[2:]


if __name__ == "__main__":

    args = obci_arg_parser().parse_args()
    args.func(args)
