#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher_messages import message_templates, error_codes
from obci_control_peer import OBCIControlPeer, basic_arg_parser
from peer import peer_config_parser

import common.obci_control_settings as settings
import common.net_tools as net

class OBCIClient(object):

    default_timeout=5000

    def __init__(self, server_addresses, zmq_context=None):
        self.ctx = zmq_context if zmq_context else zmq.Context()

        self.server_req_socket = self.ctx.socket(zmq.REQ)
        self.server_addresses = server_addresses
        for addr in server_addresses:
            print addr
            self.server_req_socket.connect(addr)

        #self = zmq.Poller()
        #self.register(self.server_req_socket, zmq.POLLIN)
        self.poller = PollingObject()

        self.mtool = OBCIMessageTool(message_templates)


    def launch(self, launch_file=None, sandbox_dir=None, name=None, overwrites=None):
        result = self.send_create_experiment(launch_file, sandbox_dir, name, overwrites)
        print "create result:", result
        if not result:
            return result
        if result.type != "experiment_created":
            return result
        print result
        machine = result.origin_machine
        addrs = [addr for addr in result.rep_addrs if self._addr_connectable(addr, machine)]

        return self.send_start_experiment(result.rep_addrs)

    def morph(self, exp_strname, launch_file, name=None, overwrites=None, leave_on=None):
        response = self.get_experiment_contact(exp_strname)
        exp_sock = self.ctx.socket(zmq.REQ)
        if response.type == "rq_error":
            return response
        for addr in response.rep_addrs:
            exp_sock.connect(addr)


        msg = self.mtool.fill_msg('morph_to_new_scenario', launch_file=launch_file,
                                name=name, overwrites=overwrites, leave_on=leave_on)
        send_msg(exp_sock, msg)

        response, details = self.poll_recv(exp_sock, 6000)
        return response

    def _addr_connectable(self, addr, machine):
        return machine == socket.gethostname() or \
                    (net.is_ip(addr) and not net.addr_is_local(addr))

    def start_chosen_experiment(self, exp_strname):
        response = self.get_experiment_contact(exp_strname)

        if response.type == "rq_error":
            return response

        return self.send_start_experiment(response.rep_addrs)

    def send_start_experiment(self, exp_addrs):
        exp_sock = self.ctx.socket(zmq.REQ)
        for addr in exp_addrs:
            exp_sock.connect(addr)

        send_msg(exp_sock, self.mtool.fill_msg("start_experiment"))
        reply, details =  self.poll_recv(exp_sock, 20000)
        print reply
        return reply

    def force_kill_experiment(self, strname):
        pass

    def get_experiment_contact(self, strname):
        send_msg(self.server_req_socket, self.mtool.fill_msg("get_experiment_contact",
                                        strname=strname))
        response, details = self.poll_recv(self.server_req_socket, self.default_timeout)
        return response


    def ping_server(self, timeout=50):
        send_msg(self.server_req_socket, self.mtool.fill_msg("ping"))
        response, details = self.poll_recv(self.server_req_socket, timeout)

        return response

    def retry_ping(self, timeout=50):
        response, details = self.poll_recv(self.server_req_socket, timeout)
        return response

    def send_create_experiment(self, launch_file=None, sandbox_dir=None, name=None, overwrites=None):

        send_msg(self.server_req_socket, self.mtool.fill_msg("create_experiment",
                            launch_file=launch_file, sandbox_dir=sandbox_dir, name=name,
                            overwrites=overwrites))

        response, details = self.poll_recv(self.server_req_socket, 5000)
        return response

    def send_list_experiments(self):
        send_msg(self.server_req_socket, self.mtool.fill_msg("list_experiments"))

        response, details = self.poll_recv(self.server_req_socket, 4000)
        return response

    def get_experiment_details(self, strname, peer_id=None):
        response = self.get_experiment_contact(strname)

        if response.type == "rq_error":
            return response

        sock = self.ctx.socket(zmq.REQ)
        for addr in response.rep_addrs:
            sock.connect(addr)

        if peer_id:
            send_msg(sock, self.mtool.fill_msg("get_peer_info", peer_id=peer_id))
        else:
            send_msg(sock, self.mtool.fill_msg("get_experiment_info"))
        response, details = self.poll_recv(sock, 2000)

        return response

    def configure_peer(self, exp_strname, peer_id, config_overrides, override_files=None):
        response = self.get_experiment_contact(exp_strname)

        if response.type == "rq_error":
            return response


        sock = self.ctx.socket(zmq.REQ)
        for addr in response.rep_addrs:
            sock.connect(addr)

        if override_files:
            send_msg(sock, self.mtool.fill_msg("get_peer_info", peer_id=peer_id))
            response, details = self.poll_recv(sock, 2000)
            if response.type is 'rq_error':
                return response

        msg = self.mtool.fill_msg("update_peer_config", peer_id=peer_id,
                                                                **config_overrides)

        send_msg(sock, msg)
        print msg
        response, details = self.poll_recv(sock, 2000)
        return response

            # "update_peer_config" : dict(peer_id='', local_params='',
            #                 external_params='', launch_dependencies='', config_sources=''),


    def kill_exp(self, strname, force=False):
        send_msg(self.server_req_socket,
                self.mtool.fill_msg("kill_experiment", strname=strname))
        return self.poll_recv(self.server_req_socket, 2000)[0]


    def srv_kill(self):
        send_msg(self.server_req_socket,
                self.mtool.fill_msg("kill"))
        return self.poll_recv(self.server_req_socket, 2000)[0]

    def join_experiment(self, strname, peer_id, path):
        response = self.get_experiment_contact(strname)

        if response.type == "rq_error":
            return response

        sock = self.ctx.socket(zmq.REQ)
        for addr in response.rep_addrs:
            sock.connect(addr)

        send_msg(sock, self.mtool.fill_msg("join_experiment",
                                        peer_id=peer_id, path=path, peer_type='obci_peer'))
        response, details = self.poll_recv(sock, 4000)
        return response


    def get_tail(self, strname, peer_id, len_):
        response = self.get_experiment_contact(strname)

        if response.type == "rq_error":
            return response

        sock = self.ctx.socket(zmq.REQ)
        for addr in response.rep_addrs:
            sock.connect(addr)

        send_msg(sock, self.mtool.fill_msg("get_tail", peer_id=peer_id, len=len_))
        response, details = self.poll_recv(sock, 4000)

        return response

    def poll_recv(self, socket, timeout):
        result, details = self.poller.poll_recv(socket, timeout)
        if result:
            result = self.mtool.unpack_msg(result)

        return result, details