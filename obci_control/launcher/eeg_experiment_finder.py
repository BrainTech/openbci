#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq

from launcher.obci_client import OBCIClient
from launcher.obci_script import client_server_prep
import common.net_tools as net
from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

class EEGExperimentFinder(object):
    def __init__(self, srv_addrs, ctx):
        self.client = OBCIClient(srv_addrs, ctx)#client_server_prep()
        self.poller = PollingObject()
        self.mtool = OBCIMessageTool(message_templates)
        self._amplified_cache = {}

    def _running_experiments(self):
        exp_list = self.client.send_list_experiments()
        if not exp_list:
            print "FAAAAIL"
            return None

        exps = exp_list.exp_data
        running = []
        for exp in exps.values():
            if exp['status_name'] == 'running':
                running.append(exp)
        return running

    def find_amplified_experiments(self):
        running_exps = self._running_experiments()
        amplified = []
        for exp in running_exps:
            print exp['name']
            infos = self._info_amplified(exp)

            if infos is not None:
                amplified += infos

        return amplified

    def _info_amplified(self, exp_desc):
        amp_options = []
        print exp_desc['rep_addrs']
        rep_addrs = net.choose_not_local(exp_desc['rep_addrs'])
        
        if not rep_addrs:
            rep_addrs = net.choose_local(exp_desc['rep_addrs'], ip=True)
        rep_addr = rep_addrs.pop()

        pub_addrs = net.choose_not_local(exp_desc['pub_addrs'])
        if not pub_addrs:
            pub_addrs = net.choose_local(exp_desc['pub_addrs'], ip=True)
        pub_addr = pub_addrs.pop()
        print rep_addr, pub_addr

        req_sock = self.client.ctx.socket(zmq.REQ)
        req_sock.connect(rep_addr)

        send_msg(req_sock, self.mtool.fill_msg('get_experiment_info'))
        res, details = self.poll_recv(req_sock, 4000)

        if not res:
            print "Connection failed (experiment", exp_desc['name'], ")"
            return None
        exp_info = res#json.loads(res)

        peer_list = exp_info.peers
        if not self._has_mx(peer_list):
            print "no mx"
            return None
        
        maybe_amps = self._amp_like_peers(peer_list)
        if not maybe_amps:
            print "no amp"
            return None
        
        for peer in maybe_amps:
            info, params = self._get_amp_info(req_sock, peer)
            if not self._is_amplifier(info, params):
                print "ble"
                continue
            else:
                exp_data = self._create_exp_data(exp_info, info, params.param_values,rep_addr, pub_addr)
                amp_options.append(exp_data)
        return amp_options

    def _get_amp_info(self, exp_sock, peer_id):
        send_msg(exp_sock, self.mtool.fill_msg('get_peer_info', peer_id=peer_id))
        info, details = self.poll_recv(exp_sock, 4000)

        send_msg(exp_sock, self.mtool.fill_msg('get_peer_param_values', peer_id=peer_id))
        params, details = self.poll_recv(exp_sock, 4000)
        if not info or not params:
            print "get_peer_info failed", peer_id, details
            return None, None
        return info, params


    def _is_amplifier(self, peer_info, peer_params):
        info = peer_info
        peer_id = info.peer_id
        
        if not info.peer_type == 'obci_peer':
            print "not obci_peer", peer_id
            return False
        
        params = peer_params.param_values
        if not 'channels_info' in params or\
            not 'active_channels' in params:
            print "no channels_info"
            return False

        return True

    def _create_exp_data(self, exp_info, peer_info, params, rep_addr, pub_addr):
        data = {}
        data['amplifier_params'] = params
        data['amplifier_peer_info'] = peer_info.dict()
        data['experiment_info'] = exp_info.dict()
        data['rep_addr'] = rep_addr
        data['pub_addr'] = pub_addr
        return data

    def _has_mx(self, peer_list):
        return [peer for peer in peer_list if peer.startswith('mx')] != []

    def _amp_like_peers(self, peer_list):
        return [peer for peer in peer_list if peer.startswith('amplifier')]

    def poll_recv(self, socket, timeout):
        result, details = self.poller.poll_recv(socket, timeout)
        if result:
            result = self.mtool.unpack_msg(result)
        
        return result, details

class AmpExperimentInfo(object):
    def __init__(self, exp_info, amp_info, rep_addr, pub_addr):
        self.dict_info = {}

if __name__ == '__main__':
    finder = EEGExperimentFinder(['tcp://127.0.0.1:54654'], zmq.Context())
    exps = finder.find_amplified_experiments()
    print exps
    desc = json.dumps(exps, indent=4)
    print desc
