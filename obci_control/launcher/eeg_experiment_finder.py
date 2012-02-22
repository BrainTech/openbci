#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import time
import socket

import common.net_tools as net
from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher.launcher_messages import message_templates, error_codes

import launcher.launcher_logging as logger
from common.obci_control_settings import PORT_RANGE

LOGGER = logger.get_logger("eeg_experiment_finder", "info")

class EEGExperimentFinder(object):
    def __init__(self, srv_addrs, ctx, client_push_address, nearby_servers):
        self.ctx = ctx
        self.server_req_socket = self.ctx.socket(zmq.REQ)
        for addr in srv_addrs:
            self.server_req_socket.connect(addr)

        self.poller = PollingObject()
        self.mtool = OBCIMessageTool(message_templates)
        self.nearby_servers = nearby_servers
        self._amplified_cache = {}

    def _running_experiments(self):
        send_msg(self.server_req_socket, self.mtool.fill_msg("list_experiments"))
        exp_list, details = self.poll_recv(self.server_req_socket, 2000)
        if not exp_list:
            LOGGER.error("Connection to obci_server failed. (list_experiments)")
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
            LOGGER.info("Found running experiment: " + str(exp['name']))
            infos = self._info_amplified(exp)

            if infos is not None:
                print "Found experiments...", str(infos)[:500]
                amplified += infos

        return amplified

    def _info_amplified(self, exp_desc):
        amp_options = []
        LOGGER.info("Processing experiment "+ str(exp_desc['name']) +\
                                     "w/ addr: " + str(exp_desc['rep_addrs']))

        rep_addrs = net.choose_not_local(exp_desc['rep_addrs'])

        if not rep_addrs:
            rep_addrs = net.choose_local(exp_desc['rep_addrs'], ip=True)

        rep_addr = rep_addrs.pop()

        pub_addrs = net.choose_not_local(exp_desc['pub_addrs'])
        if not pub_addrs:
            pub_addrs = net.choose_local(exp_desc['pub_addrs'], ip=True)
        pub_addr = pub_addrs.pop()

        LOGGER.info("Chosen experiment addresses: REP -- " + \
                                str(rep_addr) + ", PUB -- " + str(pub_addr))

        req_sock = self.ctx.socket(zmq.REQ)
        req_sock.connect(rep_addr)

        send_msg(req_sock, self.mtool.fill_msg('get_experiment_info'))
        res, details = self.poll_recv(req_sock, 4000)

        if not res:
            LOGGER.error("Connection failed (experiment " + exp_desc['name'] + \
                                                    "), get_experiment_info")
            return None
        exp_info = res#json.loads(res)

        peer_list = exp_info.peers
        if not self._has_mx(peer_list):
            LOGGER.info("Experiment " + exp_desc['name'] + \
                                                " does not have a multiplexer.")
            return None

        maybe_amps = self._amp_like_peers(peer_list)
        if not maybe_amps:
            LOGGER.info("Experiment "+ exp_desc['name'] + \
                                                " -- no amplifier.")
            return None

        for peer in maybe_amps:
            info, params = self._get_amp_info(req_sock, peer)
            if not self._is_amplifier(info, params):
                LOGGER.info("Experiment "+ exp_desc['name'] + \
                                " -- peer " + str(peer) + "is not an amplifier.")
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
            LOGGER.error("get_peer_info failed " + str(peer_id) + "  " + str(details))
            return None, None
        return info, params


    def _is_amplifier(self, peer_info, peer_params):
        info = peer_info
        peer_id = info.peer_id

        if not info.peer_type == 'obci_peer':
            LOGGER.info("Peer " + str(peer_id) + "  not obci_peer")
            return False

        params = peer_params.param_values
        if not 'channels_info' in params or\
            not 'active_channels' in params:
            LOGGER.info('Peer  ' + str(peer_id) + "  no channels_info param.")
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

def find_eeg_experiments_and_push_results(ctx, srv_addrs, rq_message, nearby_servers):
    finder = EEGExperimentFinder(srv_addrs, ctx, rq_message.client_push_address, nearby_servers)
    exps = finder.find_amplified_experiments()
    mpoller = PollingObject()

    other_exps_pull = ctx.socket(zmq.PULL)
    # ifname = net.server_ifname()
    # my_addr = net.ext_ip(ifname=ifname)
    my_addr = socket.gethostname()
    port = other_exps_pull.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)
    my_push_addr = my_addr + ':' + str(port)
    print "my exp_data pull: ", my_push_addr
    checked = rq_message.checked_srvs
    if not isinstance(checked, list):
        checked = []
    checked.append(my_addr)
    nearby_servers = [ip for ip in nearby_servers if ip not in checked]

    for srv_ip in nearby_servers:
        if socket.gethostbyaddr(srv_ip)[0] == socket.gethostname() or\
                socket.gethostbyaddr(srv_ip)[0].startswith(socket.gethostname() + '.'):  #w/ domain
            print "own addr"
            continue
        addr  = 'tcp://' + srv_ip + ':' + net.server_rep_port()
        req = ctx.socket(zmq.REQ)
        req.connect(addr)
        send_msg(req, finder.mtool.fill_msg('find_eeg_experiments',
                                        client_push_address='tcp://'+my_push_addr,
                                        checked_srvs=checked))
        checked.append(srv_ip)
        msg, details = mpoller.poll_recv(req, 5000)
        if not msg:
            req.close()
            continue
        print msg
        msg = finder.mtool.unpack_msg(msg)
        if msg.type == 'rq_ok':
            result, details = mpoller.poll_recv(other_exps_pull, 10000)
            if not result:
                req.close()
                continue
            result = finder.mtool.unpack_msg(result)
            if not result:
                print "ble, ", srv_ip
                req.close()
                continue
            if result.type == 'eeg_experiments':
                print "GOT EXPERIMENTS from", srv_ip
                exps += result.experiment_list
        req.close()

    print "return to:  ", rq_message.client_push_address
    to_client = ctx.socket(zmq.PUSH)
    to_client.connect(rq_message.client_push_address)

    send_msg(to_client, finder.mtool.fill_msg('eeg_experiments',
                                    experiment_list=exps))
    print "sent exp data...", str(exps)[:500], '[...]'
    time.sleep(0.2)


if __name__ == '__main__':
    finder = EEGExperimentFinder(['tcp://127.0.0.1:54654'], zmq.Context(), 'tcp://127.0.0.1:12345', [])
    exps = finder.find_amplified_experiments()
    desc = json.dumps(exps, indent=4)
    print desc
