#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import socket
import time

from obci.control.common.message import OBCIMessageTool
import obci.control.common.net_tools as net

from obci.control.launcher.launcher_messages import message_templates

from obci.control.launcher.plain_tcp_handling import make_unicode_netstring, recv_unicode_netstring


mtool = OBCIMessageTool(message_templates)

def send_and_receive(host, port, msg):
    netstr = make_unicode_netstring(msg)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    wfile = None
    rfile = None

    rec_msg = None
    try:
        # Connect to server and send data
        sock.connect((host, port))
        rfile = sock.makefile('rb', -1)
        wfile = sock.makefile('wb', 0)
        wfile.write(netstr)

        # Receive data from the server and shut down
        received = recv_unicode_netstring(rfile)
        print received
        print received.__class__, received[0], received[-1]
        rec_msg = mtool.unpack_msg(received)

    finally:
        sock.close()
        if wfile is not None:
            wfile.close()
        if rfile is not None:
            rfile.close()
    return rec_msg


def get_eeg_experiments(host, port):

    msg = mtool.fill_msg("find_eeg_experiments")
    response = send_and_receive(host, port, msg)

    if response is None:
        print "FAIL."
        return

    if response.type == 'rq_error':
        print 'BLEEEEEEEEE'
    else:
        print ':-))))'

    if response.experiment_list:
        exp = response.experiment_list[0]
        # print exp
        host, port = exp['tcp_addrs'][0]
        msg = mtool.fill_msg("join_experiment", peer_id="blebleble")
        print "sending join to exp ", host, port
        response = send_and_receive(host, port, msg)
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"



def get_eeg_amplifiers(host, port):
    msg = mtool.fill_msg("find_eeg_amplifiers", amplifier_types=['bt', 'usb', 'virtual'])
    response = send_and_receive(host, port, msg)

    if response is None:
        print "FAIL."
        return

    if response.type == 'rq_error':
        print 'BLEEEEEEEEE2', response
    else:
        print '\n\n****************************************************************\n\n'
        amp =  response.amplifier_list
        if amp:
            # first from the amplifier list
            exp = amp[0]
            # fill amplifier params
            params = exp['amplifier_params']
            params['sampling_rate'] = '128'
            params['active_channels'] = '1;2;3;4'
            params['channel_names'] = 'aaa;bbb;xxx;fff'
            del params['channels_info']

            # request for experiment launch
            msg = mtool.fill_msg('start_eeg_signal', amplifier_params=params, name='HELL YEAH',
                                launch_file=exp['experiment_info']['launch_file_path'], client_push_address='')
            response= send_and_receive(host, port, msg)

            if response is None:
                print "start eeg signal failed :-("

            elif response.type == "starting_experiment":
                msg = mtool.fill_msg("get_experiment_contact", strname=response.sender)
                contact = send_and_receive(host, port, msg)

                if contact is None:
                    print "could not contact experment :/"
                    return
                elif contact.type == "experiment_contact":
                    # now we can try to join experiment
                    ip, port = contact.tcp_addrs[0]
                    _try_join_experiment(ip, port, "lame_test_script")



def _try_join_experiment(host, port, peer_id):
    trials = 5
    msg = mtool.fill_msg("join_experiment", peer_id=peer_id)
    success = False
    while not success and trials > 0:
        result = send_and_receive(host, port, msg)
        if result is None:
            print "damn this network, could not contact experiment"

        elif result.type == "rq_error":
            if result.err_code == "mx_not_running":
                print "Multiplexer has not yet started!"
            elif result.err_code == "peer_id_in_use":
                print "PEER ID already exists."
                break
        else:
            print "SUCCESS"
            success = True
        time.sleep(0.3)
        trials -= 1





if __name__ == '__main__':
    get_eeg_experiments('127.0.0.1', int(net.server_tcp_proxy_port()))#'172.16.53.135'
    get_eeg_amplifiers('127.0.0.1', int(net.server_tcp_proxy_port()))#'172.16.53.135'
    #59336
