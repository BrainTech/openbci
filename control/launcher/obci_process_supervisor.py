#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import subprocess
import argparse
import time

import zmq
import socket

from obci.control.common.message import OBCIMessageTool, send_msg, recv_msg
from obci.control.launcher.launcher_messages import message_templates
import obci.control.common.net_tools as net
import obci.control.common.obci_control_settings as settings
from obci.control.peer.config_defaults import CONFIG_DEFAULTS

from obci.control.launcher.obci_control_peer import OBCIControlPeer, basic_arg_parser
import obci.control.launcher.launcher_tools as launcher_tools

from obci.utils.openbci_logging import log_crash

from subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO, RETURNCODE
from process_io_handler import DEFAULT_TAIL_RQ

TEST_PACKS = 100000

class OBCIProcessSupervisor(OBCIControlPeer):
    msg_handlers = OBCIControlPeer.msg_handlers.copy()

    @log_crash
    def __init__(self, sandbox_dir,
                                        source_addresses=None,
                                        source_pub_addresses=None,
                                        rep_addresses=None,
                                        pub_addresses=None,
                                        experiment_uuid='',
                                        name='obci_process_supervisor'):

        self.peers = {}
        self.status = launcher_tools.READY_TO_LAUNCH
        self.source_pub_addresses = source_pub_addresses
        self.machine = socket.gethostname()
        self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR
        self.ctx = zmq.Context()
        self.mx_data = self.set_mx_data()
        self.env = self.peer_env(self.mx_data)
        self.launch_data = []
        self.peer_order = []
        self._running_peer_order = []
        self._current_part = None
        self.experiment_uuid = experiment_uuid
        self.peers_to_launch = []
        self.processes = {}
        self.restarting = []
        self.rqs = 0
        self._nearby_machines = net.DNS()

        self.test_count = 0

        super(OBCIProcessSupervisor, self).__init__(
                                            source_addresses=source_addresses,
                                            rep_addresses=rep_addresses,
                                            pub_addresses=pub_addresses,
                                            name=name)
        self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid, logger=self.logger)


    def peer_type(self):
        return "obci_process_supervisor"

    def net_init(self):
        self.source_sub_socket = self.ctx.socket(zmq.SUB)
        self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

        self._all_sockets.append(self.source_sub_socket)

        if self.source_pub_addresses:
            for addr in self.source_pub_addresses:
                self.source_sub_socket.connect(addr)

        (self.config_server_socket, self.cs_addresses) = self._init_socket([], zmq.PULL)
        # self.config_server_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.cs_addr = net.choose_local(self.cs_addresses)
        if not self.cs_addr:
            self.cs_addr = net.choose_not_local(self.cs_addresses)[0]
        else:
            self.cs_addr = self.cs_addr[0]

        self._all_sockets.append(self.config_server_socket)

        super(OBCIProcessSupervisor, self).net_init()

    def params_for_registration(self):
        mx_data = None
        if None not in self.mx_data:
            mx_data = [self.mx_addr_str(((socket.gethostname(), self.mx_data[0][1]), self.mx_data[1])), self.mx_data[1]]
        return dict(pid=os.getpid(), machine=self.machine,
                    mx_data=mx_data)

    def custom_sockets(self):
        return [self.source_sub_socket, self.config_server_socket]


    def _handle_registration_response(self, response):
        self.launch_data = response.params['launch_data']
        self.peers_to_launch = list(self.launch_data.keys())
        self.peer_order = response.params['peer_order']
        for part in self.peer_order:
            self._running_peer_order.append(list(part))
        self.logger.info("RECEIVED LAUNCH DATA: %s", self.launch_data)


    def set_mx_data(self):

        src_ = net.choose_not_local(self.source_pub_addresses)[:1]
        if not src_:
            src_ = net.choose_local(self.source_pub_addresses, ip=True)[:1]
        src = src_[0]
        src = src[6:].split(':')[0]

        if src == socket.gethostname():
            sock = self.ctx.socket(zmq.REP)
            port = str(sock.bind_to_random_port("tcp://127.0.0.1",
                                            min_port=settings.PORT_RANGE[0],
                                            max_port=settings.PORT_RANGE[1]))
            sock.close()
            return ('0.0.0.0', port), "" #empty passwd
        else:
            return None, None

    def mx_addr_str(self, mx_data):
        if mx_data[0] is None:
            return None
        addr, port = mx_data[0]
        self.logger.info("mx addr str:  " + addr + ':' + str(port))
        return addr + ':' + str(port)


    def peer_env(self, mx_data):

        if mx_data[0] is None:
            return None

        env = os.environ.copy()
        addr, port = mx_data[0]
        if addr == '0.0.0.0':
            addr = socket.gethostname()

        _env = {
            "MULTIPLEXER_ADDRESSES": addr + ':' + str(port),
            "MULTIPLEXER_PASSWORD": '',#mx_data[1],
            "MULTIPLEXER_RULES": launcher_tools.mx_rules_path()
        }
        env.update(_env)
        return env

    @msg_handlers.handler("start_mx")
    def handle_start_mx(self, message, sock):
        if 'mx' in self.launch_data and self.mx_data[0] is not None:
            self.logger.info("..starting multiplexer")
            self.peer_order.remove(['mx'])
            self.peers_to_launch.remove('mx')
            path = launcher_tools.mx_path()

            args = ['run_multiplexer', self.mx_addr_str(
                                (('0.0.0.0', self.mx_data[0][1]), self.mx_data[1])),
                    '--multiplexer-password', self.mx_data[1],
                    '--rules', launcher_tools.mx_rules_path()]
            proc, details = self._launch_process(path, args, 'multiplexer', 'mx',
                                                env=self.env)
            self.processes['mx'] = proc
            if proc is not None:
                self.mx = proc


    @msg_handlers.handler("start_peers")
    def handle_start_peers(self, message, sock):
        self.logger.info("start peers --  my mx_data: %s, received mx_data: %s",
                                        self.mx_data, message.mx_data)
        if 'mx' not in self.launch_data:
            mx_addr = message.mx_data[1].split(':')
            mx_addr[1] = int(mx_addr[1])
            md = list(self.mx_data)
            md[0] = tuple(mx_addr)
            self.mx_data = tuple(md)
            self.env = self.peer_env(self.mx_data)
        if message.add_launch_data:
            if self.machine in  message.add_launch_data:
                self._launch_processes(message.add_launch_data[self.machine])
        else:
            self._launch_processes(self.launch_data)


    @msg_handlers.handler("manage_peers")
    def handle_manage_peers(self, message, sock):
        if not message.receiver == self.uuid:
            return
        message.kill_peers.append('config_server')

        message.start_peers_data['config_server'] = dict(self.launch_data['config_server'])
        restore_config = [peer for peer in self.processes if peer not in message.kill_peers]
        for peer in message.kill_peers:
            proc = self.processes.get(peer, None)
            if not proc:
                self.logger.error("peer to kill not found: %s", peer)
                continue
            self.logger.info("MORPH:  KILLING %s ", peer)
            proc.kill_with_force()
            self.logger.info("MORPH:  KILLED %s ", peer)
            del self.processes[peer]
            del self.launch_data[peer]

        for peer, data in message.start_peers_data.iteritems():
            self.launch_data[peer] = data
        self.restarting = [peer for peer in message.start_peers_data if peer in message.kill_peers]

        self._launch_processes(message.start_peers_data, restore_config=restore_config)

    def _launch_processes(self, launch_data, restore_config=[]):
        proc, details = None, None
        success = True
        path, args = None, None

        self.status = launcher_tools.LAUNCHING

        ldata = []
        if 'config_server' in launch_data:
            ldata.append(('config_server', launch_data['config_server']))
        if 'amplifier' in launch_data:
            ldata.append(('amplifier', launch_data['amplifier']))
        for peer, data in launch_data.iteritems():
            if (peer, data) not in ldata:
                ldata.append((peer, data))

        for peer, data in ldata:#self.launch_data.iteritems():
            wait = 0
            if peer.startswith('mx'):
                continue
            p = os.path.expanduser(data['path'])
            if not os.path.isabs(p):
                path = os.path.join(launcher_tools.obci_root(), p)
            else:
                path = os.path.realpath(p)

            dirname = os.path.dirname(path)
            if not launcher_tools.obci_root() in dirname:
                launcher_tools.update_pythonpath(dirname)
                launcher_tools.update_obci_syspath(dirname)
                self.env.update({"PYTHONPATH" : os.environ["PYTHONPATH"]})

                self.logger.info("PYTHONPATH UPDATED  for " + peer +\
                         "!!!!!!!!   " + str(self.env["PYTHONPATH"]))
            args = data['args']
            args = self._attach_base_config_path(path, args)
            args += ['-p', 'experiment_uuid', self.experiment_uuid]
            if peer.startswith('config_server'):
                args += ['-p', 'launcher_socket_addr', self.cs_addr]

                if restore_config:
                    args += ['-p', 'restore_peers', ' '.join(restore_config)]
                wait = 0.4
            if "log_dir" in args:
                idx = args.index("log_dir") + 1
                log_dir = args[idx]
                log_dir = os.path.join(log_dir, self.name)
                args[idx] = log_dir
            else:
                log_dir = os.path.join(CONFIG_DEFAULTS["log_dir"], self.name)
                args += ['-p', 'log_dir', log_dir]
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            proc, details = self._launch_process(path, args, data['peer_type'],
                                                        peer, env=self.env, capture_io=NO_STDIO)
            if proc is not None:
                self.processes[peer] = proc
            else:
                success = False
                break
            time.sleep(wait)
        if success:
            send_msg(self._publish_socket, self.mtool.fill_msg("all_peers_launched",
                                                    machine=self.machine))
        else:
            self.logger.error("OBCI LAUNCH FAILED")
            send_msg(self._publish_socket, self.mtool.fill_msg("obci_launch_failed",
                                                    machine=self.machine, path=path,
                                                    args=args, details=details))
            self.processes = {}
            self.subprocess_mgr.killall(force=True)


    def _launch_process(self, path, args, proc_type, name,
                                    env=None, capture_io=NO_STDIO):
        self.logger.debug("launching..... %s %s", path, args)
        proc, details = self.subprocess_mgr.new_local_process(path, args,
                                                        proc_type=proc_type,
                                                        name=name,
                                                        monitoring_optflags=RETURNCODE,
                                                        capture_io=capture_io,
                                                        env=env)

        if proc is None:
            self.logger.error("process launch FAILED: %s --- %s",
                                                                path, str(args))
            send_msg(self._publish_socket, self.mtool.fill_msg("launch_error",
                                            sender=self.uuid,
                                            details=dict(machine=self.machine, path=path, args=args,
                                                        error=details, peer_id=name)))
        else:
            self.logger.info("process launch success:" +\
                                 path + str(args) + str(proc.pid))
            send_msg(self._publish_socket, self.mtool.fill_msg("launched_process_info",
                                            sender=self.uuid,
                                            machine=self.machine,
                                            pid=proc.pid,
                                            proc_type=proc_type, name=name,
                                            path=path,
                                            args=args))
        return proc, details

    def _attach_base_config_path(self, launch_path, launch_args):
        peer_id = launch_args[0]
        base = launch_path.rsplit('.', 1)[0]
        ini = '.'.join([base, 'ini'])
        return [peer_id, ini] + launch_args[1:]


    @msg_handlers.handler("get_tail")
    def handle_get_tail(self, message, sock):
        lines = message.len if message.len else DEFAULT_TAIL_RQ
        peer = message.peer_id
        if peer not in self.launch_data:
            return
        experiment_id = self.launch_data[peer]['experiment_id']
        txt = self.processes[peer].tail_stdout(lines=lines)
        send_msg(self._publish_socket, self.mtool.fill_msg("tail", txt=txt,
                                                    sender=self.uuid,
                                                    experiment_id=experiment_id,
                                                peer_id=peer))


    @msg_handlers.handler("experiment_finished")
    def handle_experiment_finished(self, message, sock):
        pass

    @msg_handlers.handler("morph_to_new_scenario")
    def handle_morph(self, message, sock):
        pass


    @msg_handlers.handler('nearby_machines')
    def handle_nearby_machines(self, message, sock):
        self._nearby_machines.mass_update(message.nearby_machines)


    @msg_handlers.handler("stop_all")
    def handle_stop_all(self, message, sock):
        self.subprocess_mgr.killall(force=True)

    @msg_handlers.handler("_kill_peer")
    def handle_kill_peer(self, message, sock):
        proc = self.processes.get(message.peer_id, None)
        if proc is not None: # is on this machine
            proc.kill_with_force()

    @msg_handlers.handler("rq_ok")
    def handle_rq_ok(self, message, sock):
        self.rqs += 1
        # print "--> ", self.rqs
        if self.rqs == 10000:

            self.logger.debug("GOT %s %s", str(self.rqs), "messages!")
            self.rqs = 0

    @msg_handlers.handler("experiment_launch_error")
    def handle_experiment_launch_error(self, message, sock):
        self.subprocess_mgr.killall(force=True)

    @msg_handlers.handler("dead_process")
    def handle_dead_process(self, message, sock):
        proc = self.subprocess_mgr.process(message.machine, message.pid)
        if proc is not None:
            proc.mark_delete()
            name = proc.name
            if (proc.proc_type == 'obci_peer' or proc.proc_type == 'multiplexer') and \
                                not (name in self.restarting and message.status[0] == 'terminated'):
                self.logger.info("KILLLING! sending obci_peer_"
                                "dead for process %s", proc.name)
                send_msg(self._publish_socket, self.mtool.fill_msg("obci_peer_dead",
                                                sender=self.uuid,
                                                sender_ip=self.machine,
                                                peer_id=proc.name,
                                                path=proc.path,
                                                status=proc.status()
                                                ))
            if name in self.restarting:
                self.restarting.remove(name)

    @msg_handlers.handler("obci_peer_registered")
    def handle_obci_peer_registered(self, message, sock):
        send_msg(self._publish_socket, message.SerializeToString())

    @msg_handlers.handler("obci_peer_params_changed")
    def handle_obci_peer_params_changed(self, message, sock):
        send_msg(self._publish_socket, message.SerializeToString())

    @msg_handlers.handler("obci_peer_ready")
    def handle_obci_peer_ready(self, message, sock):
        self.logger.info("got! " + message.type)
        send_msg(self._publish_socket, message.SerializeToString())


    @msg_handlers.handler("obci_control_message")
    def handle_obci_control_message(self, message, sock):
        # ignore :)
        pass

    @msg_handlers.handler("obci_peer_dead")
    def handle_obci_control_message(self, message, sock):
        # ignore :)
        pass

    @msg_handlers.handler("process_supervisor_registered")
    def handle_supervisor_registered(self, messsage, sock):
        # also ignore
        pass

    def cleanup_before_net_shutdown(self, kill_message, sock=None):
        self.processes = {}
        self.subprocess_mgr.killall(force=True)

    def clean_up(self):
        self.logger.info("cleaning up")

        self.processes = {}
        self.subprocess_mgr.killall(force=True)
        self.subprocess_mgr.delete_all()

    def _crash_extra_data(self, exception=None):
        data = super(OBCIExperiment, self)._crash_extra_data(exception)
        data.update({
            'experiment_uuid': self.experiment_uuid,
            'name': self.name
            })
        return data


def process_supervisor_arg_parser():
    parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
                    description='A process supervisor for OBCI Peers')
    parser.add_argument('--sv-pub-addresses', nargs='+',
                    help='Addresses of the PUB socket of the supervisor')
    parser.add_argument('--sandbox-dir',
                    help='Directory to store temporary and log files')

    parser.add_argument('--name', default='obci_process_supervisor',
                    help='Human readable name of this process')
    parser.add_argument('--experiment-uuid', help='UUID of the parent obci_experiment')
    return parser


if __name__ == '__main__':
    parser = process_supervisor_arg_parser()
    args = parser.parse_args()

    process_sv = OBCIProcessSupervisor(args.sandbox_dir,
                            source_addresses=args.sv_addresses,
                            source_pub_addresses=args.sv_pub_addresses,
                            rep_addresses=args.rep_addresses,
                            pub_addresses=args.pub_addresses,
                            experiment_uuid=args.experiment_uuid,
                            name=args.name)
    process_sv.run()
