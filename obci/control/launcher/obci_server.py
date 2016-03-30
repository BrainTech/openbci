#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import threading
import uuid
import argparse
import os.path
import sys
import json
import time
import socket

import zmq

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg
from obci.control.launcher.launcher_messages import message_templates, error_codes
from obci.control.launcher.launcher_tools import module_path
from obci.control.launcher.eeg_experiment_finder import find_eeg_experiments_and_push_results,\
find_new_experiments_and_push_results
from obci.control.launcher.start_eeg_signal import start_eeg_signal_experiment

from obci_control_peer import OBCIControlPeer, basic_arg_parser
import obci.control.common.obci_control_settings as settings
import obci.control.common.net_tools as net
from obci.control.peer import peer_cmd

import obci.control.launcher.obci_experiment as obci_experiment
import obci.control.launcher.obci_process_supervisor as obci_process_supervisor
import obci.control.launcher.subprocess_monitor as subprocess_monitor
from obci.control.launcher.subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO

from obci.control.launcher.server_scanner import update_nearby_servers, broadcast_server

import obci.control.launcher.twisted_tcp_handling as twisted_tcp_handling

from obci.utils.openbci_logging import log_crash

REGISTER_TIMEOUT = 6

class OBCIServer(OBCIControlPeer):

    msg_handlers = OBCIControlPeer.msg_handlers.copy()

    @log_crash
    def __init__(self, rep_addresses=None, pub_addresses=None, name='obci_server'):

        self.experiments = {}
        self.exp_process_supervisors = {}
        self._nearby_servers = net.DNS()
        super(OBCIServer, self).__init__( None, rep_addresses,
                                                          pub_addresses,
                                                          name)

        self.machine = socket.gethostname()

        self.rep_port = int(net.server_rep_port())
        self.pub_port = int(net.server_pub_port())
        bcast_port = int(net.server_bcast_port())
        self._nearby_servers.logger = self.logger
        self._bcast_server = threading.Thread(target=broadcast_server,
                                                args=[self.uuid,
                                                    self.rep_port, self.pub_port, bcast_port])
        self._bcast_server.daemon = True
        self._bcast_server.start()

        self._nearby_updater = threading.Thread(target=update_nearby_servers,
                                                args=[self._nearby_servers,

                                                        bcast_port,
                                                        self.ctx,
                                                        self._push_addr])

        self._nearby_updater.daemon = True
        self._nearby_updater.start()
        self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid, logger=self.logger)


    def nearby_server_addrs(self):
        snap = self._nearby_servers.snapshot()
        return [srv.ip for srv in snap.values()]

    def nearby_servers(self):
        return self._nearby_servers.snapshot()


    def my_ip(self):
        addr = "127.0.1.1"
        try:
            addr = self._nearby_servers.this_addr_network()
        except Exception, e:
            self.logger.error(str(e))
        return addr

    def network_ready(self):
        # i know my network IP
        return self.my_ip() != self.machine

    def handle_socket_read_error(self, socket, error):
        if socket == self.rep_socket:
            self.logger.warning("reinitialising REP socket")
            self._all_sockets.remove(self.rep_socket)
            if socket in self.client_rq:
                self.client_rq = None
            self.rep_socket.close()#linger=0)
            self.rep_socket = None
            time.sleep(0.2)
            (self.rep_socket, self.rep_addresses) = self._init_socket(
                                        ['tcp://*:' + str(self.rep_port)], zmq.REP)
            self.rep_socket.setsockopt(zmq.LINGER, 0)
            self._all_sockets.append(self.rep_socket)
            logger.info(self.rep_addresses)

        elif socket == self.exp_rep:
            self.logger.info("reinitialising EXPERIMENT REP socket")
            self.exp_rep.close()#linger=0)

            (self.exp_rep, self.exp_rep_addrs) = self._init_socket(
                                        self.exp_rep_addrs, zmq.REP)
            self.exp_rep.setsockopt(zmq.LINGER, 0)
            self._all_sockets.append(self.exp_rep)


    def peer_type(self):
        return 'obci_server'


    def net_init(self):

        (self.exp_rep, self.exp_rep_addrs) = self._init_socket(
                                                [], zmq.REP)
        # (self.exp_pub, self.exp_pub_addrs) = self._init_socket(
        #                                         [], zmq.PUB)
        # self.exp_pub.setsockopt(zmq.LINGER, 0)
        self._all_sockets.append(self.exp_rep)
        # self._all_sockets.append(self.exp_pub)
        tcp_port = int(net.server_tcp_proxy_port())

        self._tcp_proxy_thr, tcp_port = twisted_tcp_handling.run_twisted_server(
                                                ('0.0.0.0', tcp_port),
                                            self.ctx,
                                            self.rep_addresses[0])

        self.tcp_addresses = [(self.my_ip(), tcp_port),
                                (socket.gethostname(), tcp_port)]
        super(OBCIServer, self).net_init()


    def custom_sockets(self):
        return [self.exp_rep]#, self.srv_rep, self.srv_pub]

    def clean_up(self):
        #self._tcp_srv.shutdown()
        pass

    def cleanup_before_net_shutdown(self, kill_message, sock=None):
        send_msg(self._publish_socket,#self.exp_pub,
                        self.mtool.fill_msg("kill", receiver=""))
        send_msg(self._publish_socket, self.mtool.fill_msg("launcher_shutdown",
                        sender=self.uuid))
        for sup in self.exp_process_supervisors:
            self.exp_process_supervisors[sup].kill()
        self.logger.info('sent KILL to experiments')


    def _args_for_experiment(self, sandbox_dir, launch_file, local=False, name=None, overwrites=None):

        args = ['--sv-addresses']
        args += self.exp_rep_addrs
        args.append('--sv-pub-addresses')
        # if local:
        #     addrs = net.choose_local(self.exp_pub_addrs)
        # else:
        #     addrs = net.choose_not_local(self.exp_pub_addrs)
        addrs = net.choose_local(self.pub_addresses)#self.exp_pub_addrs

        args += addrs
        exp_name = name if name else os.path.basename(launch_file)

        args += [
                    '--sandbox-dir', str(sandbox_dir),
                    '--launch-file', str(launch_file),
                    '--name', exp_name,
                    '--current-ip', self.my_ip()]
        if overwrites is not None:
            args += peer_cmd.peer_overwrites_cmd(overwrites)
        # print '{0} [{1}] -- experiment args: {2}'.format(self.name, self.peer_type(), args)
        return args

    def start_experiment_process(self, sandbox_dir, launch_file, name=None, overwrites=None):
        path = module_path(obci_experiment)

        args = self._args_for_experiment(sandbox_dir, launch_file,
                                        local=True, name=name, overwrites=overwrites)

        return self.subprocess_mgr.new_local_process(path, args,
                                            proc_type='obci_experiment',
                                            capture_io=NO_STDIO)



    def handle_register_experiment(self, message, sock):
        machine, pid = message.other_params['origin_machine'], message.other_params['pid']
        status, det = message.other_params['status_name'], message.other_params['details']
        launch_file = message.other_params['launch_file_path']
        tcp_addr = message.other_params['tcp_addrs']

        exp_proc = self.subprocess_mgr.process(machine, pid)

        if exp_proc is None:
            send_msg(sock, self.mtool.fill_msg("rq_error", err_code="experiment_not_found"))
            return

        info = self.experiments[message.uuid] = ExperimentInfo(message.uuid,
                                                            message.name,
                                                            message.rep_addrs,
                                                            message.pub_addrs,
                                                            time.time(),
                                                            machine,
                                                            pid,
                                                            status,
                                                            det,
                                                            launch_file,
                                                            tcp_addr,
                                                            self._nearby_servers.this_addr_network())

        exp_proc.registered(info)
        for addrs in [info.rep_addrs, info.pub_addrs]:
            one = addrs[0]
            port = net.port(one)
            addrs = [self._nearby_servers.this_addr_network() + ':' + str(port)] + addrs

        info_msg = self.mtool.fill_msg("experiment_created",
                                                uuid=info.uuid,
                                                name=info.name,
                                                rep_addrs=info.rep_addrs,
                                                pub_addrs=info.pub_addrs,
                                                origin_machine=info.origin_machine,
                                                status_name=status,
                                                details=det,
                                                launch_file_path=launch_file,
                                                tcp_addrs=tcp_addr)

        if self.client_rq:
            msg_type = self.client_rq[0].type
            rq_sock = self.client_rq[1]
            if msg_type == "create_experiment":
                self.client_rq = None
                send_msg(rq_sock, info_msg)

        send_msg(sock, self.mtool.fill_msg("rq_ok", params=self._nearby_servers.dict_snapshot()))
        send_msg(self._publish_socket, info_msg)

    def _handle_register_experiment_timeout(self, exp):
        self.logger.error("New experiment process failed to "
            "register before timeout" + str(exp.pid))

        if exp.returncode is None:
            exp.kill()
            exp.wait()

        msg_type = self.client_rq[0].type
        rq_sock = self.client_rq[1]
        send_msg(rq_sock, self.mtool.fill_msg("rq_error",
                                                err_code="create_experiment_error",
                                                request=vars(self.client_rq[0])))


    @msg_handlers.handler("register_peer")
    def handle_register_peer(self, message, sock):
        """Register peer"""
        if message.peer_type == "obci_client":
            send_msg(sock, self.mtool.fill_msg("rq_ok"))
        elif message.peer_type == "obci_experiment":
            self.handle_register_experiment(message, sock)
        else:
            super(OBCIServer, self).handle_register_peer(message, sock)


    @msg_handlers.handler("create_experiment")
    def handle_create_experiment(self, message, sock):

        if not self.network_ready() and self._nearby_servers.dict_snapshot():
            send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='server_network_not_ready'))
            return

        launch_file = message.launch_file
        sandbox = message.sandbox_dir
        name = message.name
        overwrites = message.overwrites

        sandbox = sandbox if sandbox else settings.DEFAULT_SANDBOX_DIR

        exp, details = self.start_experiment_process(
                                    sandbox, launch_file, name, overwrites)

        if exp is None:
            self.logger.error("failed to launch experiment "
                                "process, request: " + str(vars(message)))
            send_msg(sock, self.mtool.fill_msg("rq_error",
                                        request=vars(message),
                                err_code='launch_error', details=details))
        else:
            self.logger.info("experiment process "
                                        "launched:  {0}".format(exp.pid))
            if sock.socket_type in [zmq.REP, zmq.ROUTER]:
                self.client_rq = (message, sock)


    @msg_handlers.handler("list_experiments")
    def handle_list_experiments(self, message, sock):
        exp_data = {}
        for exp_id in self.experiments:
            exp_data[exp_id] = self.experiments[exp_id].info()

        nearby = self.nearby_servers()
        nearby_dict = {}
        for srv in nearby.values():
            nearby_dict[srv.ip] = srv.hostname
        info = '\n{'
        for srv in nearby_dict:
            info += '\n' + srv + ' : ' + nearby_dict[srv] + ','
        info += '}'
        self.logger.debug("nearby servers:  count: {0}, {1}".format(
                                            len(nearby), info))
        send_msg(sock, self.mtool.fill_msg("running_experiments",
                                                exp_data=exp_data,
                                                nearby_machines=nearby_dict))

    @msg_handlers.handler("list_nearby_machines")
    def handle_list_nearby_machines(self, message, sock):
        send_msg(sock, self.mtool.fill_msg('nearby_machines',
                                nearby_machines=self._nearby_servers.dict_snapshot()))

    def _handle_match_name(self, message, sock, this_machine=False):
        matches = self.exp_matching(message.strname)
        match = None
        msg = None
        if not matches:
            msg = self.mtool.fill_msg("rq_error", request=vars(message),
                            err_code='experiment_not_found')

        elif len(matches) > 1:
            matches = [(exp.uuid, exp.name) for exp in matches]
            msg = self.mtool.fill_msg("rq_error", request=vars(message),
                            err_code='ambiguous_exp_name',
                            details=matches)
        else:
            match = matches.pop()
            if this_machine and match.origin_machine != self.machine:
                msg = self.mtool.fill_msg("rq_error", request=vars(message),
                            err_code='exp_not_on_this_machine', details=match.origin_machine)
                match = None
        if msg and sock.socket_type in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, msg)
        return match


    @msg_handlers.handler("get_experiment_contact")
    def handle_get_experiment_contact(self, message, sock):
        self.logger.debug("##### rq contact for: %s", message.strname)

        info = self._handle_match_name(message, sock)
        if info:
            send_msg(sock, self.mtool.fill_msg("experiment_contact",
                                                uuid=info.uuid,
                                                name=info.name,
                                                rep_addrs=info.rep_addrs,
                                                pub_addrs=info.pub_addrs,
                                                tcp_addrs=info.tcp_addrs,
                                                machine=info.origin_machine,
                                                status_name=info.status_name,
                                                details=info.details))


    @msg_handlers.handler("experiment_status_change")
    def handle_experiment_status_change(self, message, sock):
        exp = self.experiments.get(message.uuid, None)
        if not exp:
            if sock.socket_type in [zmq.REP, zmq.ROUTER]:
                send_msg(sock, self.mtool.fill_msg('rq_error', err_code='experiment_not_found'))
            return
        exp.status_name = message.status_name
        exp.details = message.details
        if sock.socket_type in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, self.mtool.fill_msg('rq_ok'))

        send_msg(self._publish_socket, message.SerializeToString())

    @msg_handlers.handler("experiment_info_change")
    def handle_experiment_info_change(self, message, sock):
        exp = self.experiments.get(message.uuid, None)
        if not exp:
            self.logger.warning("UUID not found  " + message.uuid)
            if sock.socket_type in [zmq.REP, zmq.ROUTER]:
                send_msg(sock, self.mtool.fill_msg('rq_error', err_code='experiment_not_found'))
            return
        exp.name = message.name
        exp.launch_file_path = message.launch_file_path
        if sock.socket_type in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, self.mtool.fill_msg('rq_ok'))
        self.logger.info("INFO CHANGED %s", exp.launch_file_path)
        send_msg(self._publish_socket, message.SerializeToString())

    @msg_handlers.handler("experiment_transformation")
    def handle_experiment_transformation(self, message, sock):
        exp = self.experiments.get(message.uuid, None)
        if not exp:
            if sock.socket_type in [zmq.REP, zmq.ROUTER]:
                send_msg(sock, self.mtool.fill_msg('rq_error', err_code='experiment_not_found'))
            return
        exp.status_name = message.status_name
        exp.details = message.details
        exp.launch_file_path = message.launch_file
        exp.name = message.name
        if sock.socket_type in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, self.mtool.fill_msg('rq_ok'))
        send_msg(self._publish_socket, message.SerializeToString())

    def exp_matching(self, strname):
        """Match *strname* against all created experiment IDs and
        names. Return those experiment descriptions which name
        or uuid starts with strname.
        """
        match_names = {}
        for uid, exp in self.experiments.iteritems():
            if exp.name.startswith(strname):
                match_names[uid] = exp

        ids = self.experiments.keys()
        match_ids = [uid for uid in ids if uid.startswith(strname)]

        experiments = set()
        for uid in match_ids:
            experiments.add(self.experiments[uid])
        for name, exp in match_names.iteritems():
            experiments.add(exp)

        return experiments


    @msg_handlers.handler("kill_experiment")
    def handle_kill_experiment(self, message, sock):
        match = self._handle_match_name(message, sock, this_machine=True)

        if match:
            if match.kill_timer is not None:
                send_msg(sock, self.mtool.fill_msg("rq_error", err_code="already_killed",
                                    details="Experiment already shutting down"))

            elif not message.force:
                self.logger.info("sending kill to experiment "
                                        "{0} ({1})".format(match.uuid, match.name))
                send_msg(self._publish_socket,#self.exp_pub,
                        self.mtool.fill_msg("kill", receiver=match.uuid))

                send_msg(sock, self.mtool.fill_msg("kill_sent", experiment_id=match.uuid))
                pid = match.experiment_pid
                uid = match.uuid
                self.logger.info("Waiting for experiment process {0} to terminate".format(uid))
                match.kill_timer = threading.Timer(1.1,
                                    self._handle_killing_exp, args=[pid, uid])
                match.kill_timer.start()
                send_msg(self._publish_socket, self.mtool.fill_msg('kill_sent',
                    experiment_id=match.uuid
                    ))


    def _handle_killing_exp(self, pid, uid):
        proc = self.subprocess_mgr.process(self.machine, pid)
        if proc.process_is_running():
            proc.kill()
        self.logger.info("experiment {0} FINISHED".format(uid))
        proc.delete = True
        del self.experiments[uid]

        return proc.popen_obj.returncode


    @msg_handlers.handler("launch_process")
    def handle_launch_process(self, message, sock):
        if message.proc_type == 'obci_process_supervisor':
            self._handle_launch_process_supervisor(message, sock)


    def _handle_launch_process_supervisor(self, message, sock):
        sv_obj, details = self._start_obci_supervisor_process( message)

        self.logger.info("LAUNCH PROCESS SV   " + str(sv_obj) + str(details))
        if sv_obj:
            self.exp_process_supervisors[message.sender] = sv_obj
            send_msg(sock,
                    self.mtool.fill_msg("launched_process_info",
                                            sender=self.uuid, machine=self.machine,
                                            pid=sv_obj.pid, proc_type=sv_obj.proc_type,
                                            name=sv_obj.name,
                                            path=sv_obj.path))
            self.logger.info("CONFIRMED LAUNCH")
        else:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                                err_code="launch_error",
                                                details=details))
            self.logger.error("PROCESS SUPERVISOR LAUNCH FAILURE")


    @msg_handlers.handler("kill_process")
    def handle_kill_process_supervisor(self, message, sock):
        proc = self.subprocess_mgr.process(message.machine, message.pid)
        if not proc:
            send_msg(sock, self.mtool.fill_msg("rq_error", err_code="process_not_found"))
        else:
            #TODO
            name = proc.name
            proc.kill()
            proc.mark_delete()
            send_msg(sock, self.mtool.fill_msg("rq_ok"))
            del self.exp_process_supervisors[proc.name]


    @msg_handlers.handler("dead_process")
    def handle_dead_process(self, message, sock):
        proc = self.subprocess_mgr.process(message.machine, message.pid)
        if proc is not None:
            proc.mark_delete()
            status, details = proc.status()
            self.logger.warning("Process " + proc.proc_type + " dead: " +\
                             status + str(details) + proc.name + str(proc.pid))
            if proc.proc_type == 'obci_process_supervisor':
                pass
            elif proc.proc_type == 'obci_experiment':
                pass
            if status == subprocess_monitor.FAILED:
                pass


    @msg_handlers.handler("find_eeg_experiments")
    def handle_find_eeg_experiments(self, message, sock):

        if not self.network_ready() and self._nearby_servers.dict_snapshot():
            send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='server_network_not_ready'))
            return

        send_msg(sock, self.mtool.fill_msg("rq_ok"))
        finder_thr = threading.Thread(target=find_eeg_experiments_and_push_results,
                                    args=[self.ctx, self.rep_addresses,
                                        message,
                                        self._nearby_servers.copy()])
        finder_thr.daemon = True
        finder_thr.start()

    @msg_handlers.handler("find_eeg_amplifiers")
    def handle_find_new_eeg_amplifiers(self, message, sock):
        if not self.network_ready() and self._nearby_servers.dict_snapshot():
            send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='server_network_not_ready'))
            return

        send_msg(sock, self.mtool.fill_msg("rq_ok"))
        amp_thr = threading.Thread(target=find_new_experiments_and_push_results,
                                    args=[self.ctx,
                                        message])
        amp_thr.daemon = True
        amp_thr.start()

    @msg_handlers.handler("start_eeg_signal")
    def handle_start_eeg_signal(self, message, sock):
        if not self.network_ready() and self._nearby_servers.dict_snapshot():
            send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='server_network_not_ready'))
            return
        send_msg(sock, self.mtool.fill_msg("rq_ok"))
        start_thr = threading.Thread(target=start_eeg_signal_experiment,
                                        args=[self.ctx, self.rep_addresses,
                                        message])
        start_thr.daemon = True
        start_thr.start()

    def _start_obci_supervisor_process(self, rq_message):
        path = obci_process_supervisor.__file__
        path = '.'.join([path.rsplit('.', 1)[0], 'py'])
        start_params = rq_message.dict()
        start_params['path'] = path
        del start_params['type']
        del start_params['sender']
        del start_params['sender_ip']
        del start_params['receiver']
        sv_obj, details = self.subprocess_mgr.new_local_process(**start_params)
        if sv_obj is None:
            return None, details

        return sv_obj, False

    def _crash_extra_data(self, exception=None):
        import json
        data = super(OBCIServer, self)._crash_extra_data(exception)
        data.update({
            'experiments': [e.info() for e in self.experiments.values()]
            })
        return data


class ExperimentInfo(object):
    def __init__(self, uuid, name, rep_addrs, pub_addrs, registration_time,
                            origin_machine, pid, status_name=None, details=None,
                            launch_file_path=None, tcp_addrs=None, ip=None):
        self.uuid = uuid
        self.name = name
        self.rep_addrs = rep_addrs
        self.pub_addrs = pub_addrs
        self.registration_time = registration_time
        self.origin_machine = origin_machine
        self.experiment_pid = pid
        self.kill_timer = None
        self.status_name = status_name
        self.details = details
        self.launch_file_path = launch_file_path
        self.tcp_addrs = tcp_addrs
        self.ip = ip

    def from_dict(dic):
        try:
            exp = ExperimentInfo(dic['uuid'], dic['rep_addrs'], dic['pub_addrs'],
                    dic['registration_time'], dic['origin_machine'], dic['pid'])
            exp.status_name = dic.get('status_name', None)
            exp.details = dic.get('details', None)
            exp.launch_file_path = dic.get('launch_file_path', None)
            exp.tcp_addrs = dic.get('tcp_addrs', None)
            exp.ip = dic.get('ip', None)
            return exp, None
        except KeyError as e:
            return None, e.args

    @property
    def machine_ip(self):
        return self.origin_machine

    @property
    def pid(self):
        return self.experiment_pid

    def info(self):
        d = dict(uuid=self.uuid,
                name=self.name,
                rep_addrs=self.rep_addrs,
                pub_addrs=self.pub_addrs,
                registration_time=self.registration_time,
                origin_machine=self.origin_machine,
                experiment_pid=self.experiment_pid,
                status_name=self.status_name,
                details=self.details,
                launch_file_path=self.launch_file_path,
                tcp_addrs=self.tcp_addrs,
                ip=self.ip)

        return d

        
def server_arg_parser(add_help=False):
    parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
                            description="OBCI Server : manage OBCI experiments.",
                            add_help=add_help)

    parser.add_argument('--name', default='obci_server',
                       help='Human readable name of this process')
    parser.add_argument('--win-silent', help='Use pythonw instead of python', action='store_true')
    return parser  
     
     
def run_obci_server():
    parser = server_arg_parser(add_help=True)
    args = parser.parse_args()
    srv = OBCIServer(args.rep_addresses, args.pub_addresses, args.name)
    srv.run()

