#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import zmq
import time
import socket

import obci.control.common.net_tools as net
from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from obci.control.launcher.launcher_messages import message_templates, error_codes

import obci.control.launcher.launcher_logging as logger
import obci.control.launcher.launcher_tools as launcher_tools
from obci.control.common.obci_control_settings import PORT_RANGE

from obci.drivers.eeg.driver_discovery.driver_discovery import find_drivers, \
find_bluetooth_amps, find_virtual_amps, find_usb_amps

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
            if exp['status_name'] == launcher_tools.RUNNING or \
                    exp['status_name'] == launcher_tools.LAUNCHING:
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
        tcp_addrs = exp_desc['tcp_addrs']
        rep_addrs = net.choose_not_local(exp_desc['rep_addrs'])

        if not rep_addrs:
            rep_addrs = net.choose_local(exp_desc['rep_addrs'], ip=True)

        rep_addr = rep_addrs.pop()

        pub_addrs = net.choose_not_local(exp_desc['pub_addrs'])
        if not pub_addrs:
            pub_addrs = net.choose_local(exp_desc['pub_addrs'], ip=True)
        pub_addr = pub_addrs.pop()
        tcp_addr = tcp_addrs.pop()

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
        exp_info = res.dict()#json.loads(res)
        for field in ["peers_status", "details"]:
            del exp_info["experiment_status"][field]

        peer_list = exp_info["peers"]
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
                exp_data = self._create_exp_data(exp_info, info, params['param_values'],
                                            rep_addr, pub_addr, tcp_addr)
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
        info = info.dict()
        params = params.dict()
        for field in ["sender", "sender_ip", "receiver", "type", "local_params", "external_params",
                            "config_sources", "launch_dependencies"]:
            del info[field]
        return info, params


    def _is_amplifier(self, peer_info, peer_params):
        info = peer_info
        peer_id = info['peer_id']

        if not info['peer_type'] == 'obci_peer':
            LOGGER.info("Peer " + str(peer_id) + "  not obci_peer")
            return False

        params = peer_params['param_values']
        if not 'channels_info' in params or\
            not 'active_channels' in params:
            LOGGER.info('Peer  ' + str(peer_id) + "  no channels_info param.")
            return False
        return True

    def _create_exp_data(self, exp_info, peer_info, params, rep_addr, pub_addr, tcp_addr):
        data = {}
        data['amplifier_params'] = params
        data['amplifier_peer_info'] = peer_info
        data['experiment_info'] = exp_info
        data['rep_addrs'] = [rep_addr]
        data['pub_addrs'] = [pub_addr]
        data['tcp_addrs'] = [tcp_addr]
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


def _gather_other_server_results(ctx, this_addr, ip_list):
    exps = []
    if not ip_list:
        return exps
    mtool = OBCIMessageTool(message_templates)
    other_exps_pull = ctx.socket(zmq.PULL)
    port = other_exps_pull.bind_to_random_port('tcp://*',
                                            min_port=PORT_RANGE[0],
                                            max_port=PORT_RANGE[1], max_tries=500)

    my_push_addr = this_addr + ':' + str(port)
    LOGGER.info( "my exp_data pull: " + my_push_addr)

    harvester = zmq.Poller()
    harvester.register(other_exps_pull)

    reqs = {}
    for srv_ip in ip_list:

        addr  = 'tcp://' + srv_ip + ':' + net.server_rep_port()
        req = ctx.socket(zmq.REQ)
        req.connect(addr)
        send_msg(req, mtool.fill_msg('find_eeg_experiments',
                                        client_push_address='tcp://'+my_push_addr,
                                        checked_srvs=[this_addr]))
        harvester.register(req, zmq.POLLIN)
        reqs[req] = addr

    srv_responses = 0

    for i in range(len(reqs) * 50):
        socks = dict(harvester.poll(timeout=300))

        for req in socks:
            msg = recv_msg(req)
            msg = mtool.unpack_msg(msg)

            if msg.type == 'rq_ok':
                LOGGER.info("waiting for experiments from server: " + str(reqs[req]))
                harvester.unregister(req)
                req.close()

            elif msg.type == 'eeg_experiments':
                LOGGER.info("GOT EXPERIMENTS from: " + msg.sender_ip)
                exps += msg.experiment_list
                srv_responses += 1
            else:
                LOGGER.warning('strange msg:  ' + str(msg))
        if srv_responses == len(ip_list):
            print "GOT ALL eeg_experiment RESPONSES :-) [addr list:  ", ip_list, "]"
            break

    other_exps_pull.close()
    return exps


def find_eeg_experiments_and_push_results(ctx, srv_addrs, rq_message, nearby_servers):
    LOGGER = logger.get_logger("eeg_experiment_finder", "info")
    finder = EEGExperimentFinder(srv_addrs, ctx, rq_message.client_push_address, nearby_servers)
    exps = finder.find_amplified_experiments()
    mpoller = PollingObject()



    checked = rq_message.checked_srvs
    if not isinstance(checked, list):
        checked = []

    nrb = {}
    for uid, srv in nearby_servers.snapshot().iteritems():
        if srv.ip not in checked:
            nrb[uid] = srv

    if not checked and nearby_servers.dict_snapshot():
        my_addr = nearby_servers.ip(hostname=socket.gethostname())
        LOGGER.info("checking other servers")
        print [(srv.hostname, srv.ip) for srv in nrb.values()]

        ip_list = [srv.ip for srv in nrb.values() if \
                            srv.ip != my_addr]
        LOGGER.info("number of servers to query: " + str(len(ip_list)))

        exps += _gather_other_server_results(ctx, my_addr, ip_list)

    else:
        LOGGER.info("not checking other servers")

    LOGGER.info("return to:  " + rq_message.client_push_address)
    to_client = ctx.socket(zmq.PUSH)
    to_client.connect(rq_message.client_push_address)

    send_msg(to_client, finder.mtool.fill_msg('eeg_experiments', sender_ip=socket.gethostname(),
                                    experiment_list=exps))
    LOGGER.info("sent exp data... "  + str(exps)[:500] + ' [...]')
    time.sleep(0.1)

def find_new_experiments_and_push_results(ctx, rq_message):
    LOGGER = logger.get_logger("eeg_AMPLIFIER_finder", "info")

    if not rq_message.amplifier_types:
        LOGGER.info("AMPLIFIER TYPES NOT SET, FINDING ALL...")
        driv = find_drivers()
    else:
        driv = []
        for amptype in rq_message.amplifier_types:

            if amptype == 'bt' or amptype == 'bluetooth':
                driv += find_bluetooth_amps()
            elif amptype == 'usb':
                driv += find_usb_amps()
            elif amptype == 'virtual':
                driv += find_virtual_amps()

    LOGGER.info("amplifiers! return to:  " + rq_message.client_push_address)
    mtool = OBCIMessageTool(message_templates)
    to_client = ctx.socket(zmq.PUSH)
    to_client.connect(rq_message.client_push_address)

    send_msg(to_client, mtool.fill_msg('eeg_amplifiers', sender_ip=socket.gethostname(),
                                    amplifier_list=driv))
    LOGGER.info("sent amplifier data... "  + str(driv)[:500] + ' [...]')
    time.sleep(0.1)


if __name__ == '__main__':
    finder = EEGExperimentFinder(['tcp://127.0.0.1:54654'], zmq.Context(), 'tcp://127.0.0.1:12345', [])
    exps = finder.find_amplified_experiments()
    desc = json.dumps(exps, indent=4)
    print desc
