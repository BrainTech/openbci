#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse
import socket
import io

import zmq

from obci.control.common.message import  send_msg, recv_msg, PollingObject
from obci.control.launcher.launcher_messages import message_templates
import obci.control.common.net_tools as net
import obci.control.common.obci_control_settings as settings
from obci.control.peer.peer_config_serializer import PeerConfigSerializerJSON

from obci.control.launcher.obci_control_peer import OBCIControlPeer, basic_arg_parser
from subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO
from obci.control.launcher.obci_control_peer import RegistrationDescription
import subprocess_monitor

import launch_file_parser
from launch_file_serializer import serialize_scenario_json
import obci.control.launcher.launcher_tools as launcher_tools
import system_config
import obci_process_supervisor

import obci.control.peer.peer_cmd as peer_cmd

import twisted_tcp_handling

REGISTER_TIMEOUT = 25

class OBCIExperiment(OBCIControlPeer):

    msg_handlers = OBCIControlPeer.msg_handlers.copy()

    def __init__(self, sandbox_dir, launch_file=None,
                                        source_addresses=None,
                                        source_pub_addresses=None,
                                        rep_addresses=None,
                                        pub_addresses=None,
                                        name='obci_experiment',
                                        current_ip=None,
                                        launch=False,
                                        overwrites=None):

        ###TODO TODO TODO !!!!
        ###cleaner subclassing of obci_control_peer!!!
        self.source_pub_addresses = source_pub_addresses
        self.origin_machine = socket.gethostname()
        self.poller = PollingObject()
        self.launch_file = launcher_tools.obci_root_relative(launch_file)
        self.current_ip = current_ip
        self._nearby_machines = net.DNS()

        super(OBCIExperiment, self).__init__(
                                            source_addresses,
                                            rep_addresses,
                                            pub_addresses,
                                            name)

        self.name = name + ' on ' + socket.gethostname()
        
        self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR


        self.supervisors = {} #machine -> supervisor contact/other info
        self._wait_register = 0
        self._ready_register = 0
        self._kill_and_launch = None
        self._exp_extension = {}
        self.sv_processes = {} # machine -> Process objects)
        self.unsupervised_peers = {}

        self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid, logger=self.logger)

        if launch_file == 'None': # command line arg
            self._initialize_experiment_without_config()
        else:
            self.exp_config, self.status = self._initialize_experiment_config(self.launch_file, overwrites)
        self.logger.info("initialised config")
        self.status_changed(self.status.status_name, self.status.details)
        self.logger.info("status changed!!!" + self.status.status_name)

        self.mx_addr = None
        self.mx_pass = None


    def net_init(self):
        self.source_sub_socket = self.ctx.socket(zmq.SUB)
        self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

        if self.source_pub_addresses:
            for addr in self.source_pub_addresses:
                self.source_sub_socket.connect(addr)
        self._all_sockets.append(self.source_sub_socket)

        (self.supervisors_rep, self.supervisors_rep_addrs) = self._init_socket(
                                    [],
                                    zmq.REP)
        (self.supervisors_sub, self.supervisors_sub_addrs) = (self.ctx.socket(zmq.SUB), [])

        self._all_sockets.append(self.supervisors_sub)
        self._all_sockets.append(self.supervisors_rep)

        super(OBCIExperiment, self).net_init()

        self.rep_addresses.append(self._ip_based_addr(net.choose_addr(self.rep_addresses)))
        self.pub_addresses.append(self._ip_based_addr(net.choose_addr(self.pub_addresses)))

        tcp_port = 0


        self._tcp_proxy_thr, tcp_port = twisted_tcp_handling.run_twisted_server(
                                                ('0.0.0.0', tcp_port),
                                            self.ctx,
                                            self.rep_addresses[0])


        self.tcp_addresses = [(self.current_ip, tcp_port),
                                (socket.gethostname(), tcp_port)]


    def _ip_based_addr(self, other_addr):
        return 'tcp://'+str(self.current_ip)+':'+str(net.port(other_addr))

    def params_for_registration(self):
        return dict(pid=os.getpid(), origin_machine=self.origin_machine,
                status_name='', details='', launch_file_path=self.launch_file,
                tcp_addrs=[self.tcp_addresses[0]])

    def _handle_registration_response(self, response):
        self._nearby_machines.mass_update(response.params)

    def custom_sockets(self):
        return [self.source_sub_socket, self.supervisors_sub, self.supervisors_rep]

    def args_for_process_sv(self, machine, local=False):
        args = ['--sv-addresses']
        local = self._nearby_machines.is_this_machine(machine)

        a = self._ip_based_addr(net.choose_addr(self.supervisors_rep_addrs))
        if local:
            port = net.port(a)
            a = 'tcp://' + socket.gethostname() + ':' + str(port)
        # sv_rep_ = net.choose_not_local(self.supervisors_rep_addrs)
        # if not sv_rep_ or local:
        #     sv_rep_ = net.choose_local(self.supervisors_rep_addrs)

        args.append(a)#addr_to_pass) # += sv_rep_[:1]
        args.append('--sv-pub-addresses')
        a = self._ip_based_addr(net.choose_addr(self.pub_addresses))
        if local:
            port = net.port(a)
            a = 'tcp://' + socket.gethostname() + ':' + str(port)

        # pub_addrs = net.choose_not_local(self.pub_addresses)
        # if not pub_addrs or local:
        #     pub_addrs = net.choose_local(self.pub_addresses, ip=True)

        args.append(a) # += pub_addrs[:1] #self.pub_addresses
        name = self.name if self.name and self.name != 'obci_experiment' else\
                    os.path.basename(self.launch_file)
        args += [
                    '--sandbox-dir', str(self.sandbox_dir),
                    '--name', name +\
                             '-' + self.uuid.split('-',1)[0] + \
                            '-' + machine,
                    '--experiment-uuid', self.uuid
                    ]
        return args


    def _start_obci_process_supervisor(self, machine_addr):
        args = self.args_for_process_sv(machine_addr)
        proc_type = 'obci_process_supervisor'

        if machine_addr == self.origin_machine:
            path = obci_process_supervisor.__file__
            path = '.'.join([path.rsplit('.', 1)[0], 'py'])
            sv_obj, details = self.subprocess_mgr.new_local_process(path, args,
                                                            proc_type=proc_type,
                                                            capture_io=NO_STDIO)
        else:
            try:
                srv_ip = self._nearby_machines.ip(hostname=machine_addr)
            except  Exception, e:
                det = "Machine " + machine_addr +" not found, cannot launch remote process!" +\
                                    "Is obci_server running there? " +\
                                    "If yes, maybe you should wait for a few seconds and retry."
                self.logger.critical(det)
                return False, det

            conn_addr = 'tcp://' + srv_ip + ':' + net.server_rep_port()
            sv_obj, details = self.subprocess_mgr.new_remote_process(path=None,
                                                args=args, proc_type=proc_type,
                                                name=self.uuid, machine_ip=machine_addr,
                                                conn_addr=conn_addr, capture_io=NO_STDIO
                                                )
        if sv_obj is None:
            return False, details

        timeout_handler = TimeoutDescription(timeout=REGISTER_TIMEOUT,
                        timeout_method=self._handle_register_sv_timeout,
                        timeout_args=[sv_obj])
        sv_obj.set_registration_timeout_handler(timeout_handler)
        self.sv_processes[machine_addr] = sv_obj
        return sv_obj, None

    def _start_obci_process_supervisors(self, peer_machines):
        self._wait_register = len(peer_machines)
        details = None

        for machine in peer_machines:
            result, details = self._start_obci_process_supervisor(machine)

            if not result:
                self.status.set_status(launcher_tools.FAILED_LAUNCH, details)
                details = "FAILED to start supervisor: {0}".format(details)
                self.logger.error(details)
                self.status_changed(self.status.status_name, self.status.details)
                return False, details

            k = result.machine_ip
            self.sv_processes[k] = result
        return True, details

    def _send_launch_data(self):
        pass

    def _start_experiment(self):
        """
        START EXPERIMENT!!!!
        ##################################################################
        """
        result, details = self._start_obci_process_supervisors(self.exp_config.peer_machines())
        if not result:
            send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
                                                sender=self.uuid, details=details,
                                                err_code='supervisor_launch_error'))


        return result, details

    def _initialize_experiment_config(self, launch_file, overwrites=None):
        status = launcher_tools.ExperimentStatus()

        exp_config = system_config.OBCIExperimentConfig(uuid=self.uuid)
        exp_config.origin_machine = self.origin_machine
        exp_config.launch_file_path = launch_file

        result, details = self.make_experiment_config(exp_config, launch_file, status)
        if overwrites:
            try:
                for [ovr, other] in overwrites:
                    exp_config.update_peer_config(other['peer_id'], ovr)
                    if other['config_file']:
                        for f in other['config_file']:
                            exp_config.file_update_peer_config(other['peer_id'], f)
            except Exception, e:
                details = str(e)

        exp_config.status(status)
        status.details = details
        # status_changed(status.status_name, status.details)
        if not launch_file:
            self.logger.error("No launch file")
        elif not result:
            self.logger.error("- - - - - - - NEW LAUNCH FILE INVALID!!!  - - - - - - - "
                            "status: " + str(status.as_dict()) + str(details))
        return exp_config, status

    def _initialize_experiment_without_config(self):
        self.status = launcher_tools.ExperimentStatus()
        self.status.set_status(launcher_tools.NOT_READY, details="No launch_file")
        self.exp_config = system_config.OBCIExperimentConfig()
        self.exp_config.origin_machine = self.origin_machine

    def make_experiment_config(self, exp_config, launch_file, status):
        launch_parser = launch_file_parser.LaunchFileParser(
                            launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
        if not launch_file:
            return False, "Empty scenario."
        try:
            with open(launcher_tools.expand_path(launch_file)) as f:
                self.logger.info("launch file opened " + launch_file)
                launch_parser.parse(f, exp_config, apply_globals=True)
        except Exception as e:
            status.set_status(launcher_tools.NOT_READY, details=str(e))

            return False, str(e)

        #print self.exp_config
        rd, details = exp_config.config_ready()
        if rd:
            status.set_status(launcher_tools.READY_TO_LAUNCH)
        else:
            status.set_status(launcher_tools.NOT_READY, details=details)

        return True, None

    def status_changed(self, status_name, details, peers=None):
        # TODO use PUB/SUB pattern
        send_msg(self.source_req_socket, self.mtool.fill_msg('experiment_status_change',
                status_name=status_name, details=details, uuid=self.uuid, peers=peers))
        self.poller.poll_recv(self.source_req_socket, timeout=8000)


    def peer_type(self):
        return 'obci_experiment'


    @msg_handlers.handler('register_peer')
    def handle_register_peer(self, message, sock):
        """Experiment"""
        if message.peer_type == "obci_process_supervisor":

            machine, pid = message.other_params['machine'], message.other_params['pid']

            if message.other_params['mx_data'] is not None and not self.mx_addr:
                ## right now we support only one mx per obci instance
                ip = self._nearby_machines.ip(machine) if self._nearby_machines.dict_snapshot() else\
                            machine

                self.mx_addr = ip + ':' + message.other_params['mx_data'][0].split(':')[1]
                self.mx_pass = message.other_params['mx_data'][1]

            proc = self.subprocess_mgr.process(machine, pid)
            if proc is None:
                send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='process_not_found', request=message.dict()))
                return

            status, details = proc.status()
            if status != subprocess_monitor.UNKNOWN:
                send_msg(sock, self.mtool.fill_msg("rq_error",
                                err_code='process_status_invalid', request=message.dict(),
                                details=(status, details)))
                send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
                                                sender=self.uuid, details=(status, details),
                                                err_code='registration_error'))
                return
            self.logger.info("exp registration message  " + str(vars(message)))
            adr_list = [message.rep_addrs, message.pub_addrs]
            if machine != socket.gethostname():
                ip = self._nearby_machines.ip(machine)
                for i, addrs in enumerate([message.rep_addrs, message.pub_addrs]):
                    first = addrs[0]
                    port = net.port(first)
                    adr_list[i] = ['tcp://' + ip + ':' + str(port)]
            self.logger.info("addresses after filtering: %s", str(adr_list))
            desc = self.supervisors[machine] = \
                            RegistrationDescription(
                                                message.uuid,
                                                message.name,
                                                adr_list[0],
                                                adr_list[1],
                                                message.other_params['machine'],
                                                message.other_params['pid'])
            proc.registered(desc)
            a = self._choose_process_address(proc, desc.pub_addrs)
            if a is not None:
                self.supervisors_sub_addrs.append(a)
                self.supervisors_sub.setsockopt(zmq.SUBSCRIBE, "")
                self.supervisors_sub.connect(a)
                self.logger.info("Connecting to supervisor pub address {0} ({1})".format(a, machine))
            else:
                self.logger.error("Could not find suitable PUB address to connect. (supervisor on " + machine +")")

            launch_data = self.exp_config.launch_data(machine)
            order = self.exp_config.peer_order()

            send_msg(sock, self.mtool.fill_msg("rq_ok", params=dict(launch_data=launch_data,
                                                                        peer_order=order)))

            # inform observers
            send_msg(self._publish_socket, self.mtool.fill_msg("process_supervisor_registered",
                                                sender=self.uuid,
                                                machine_ip=desc.machine_ip))

            self._wait_register -= 1
            if self._wait_register == 0:
                if self._kill_and_launch:
                    kill, launch = self._kill_and_launch
                    to_launch = launch[machine]
                    to_kill = kill.get(machine, [])
                    send_msg(self._publish_socket, self.mtool.fill_msg("manage_peers",
                                                    kill_peers=to_kill, start_peers_data=to_launch,
                                                    receiver=desc.uuid))
                elif self._exp_extension:
                    ldata = {}
                    peer_id = self._exp_extension[machine][0]
                    ldata[peer_id] = self.exp_config.launch_data(machine)[peer_id]
                    send_msg(self._publish_socket, self.mtool.fill_msg("start_peers", mx_data=self.mx_args(), 
                                                    add_launch_data={machine : ldata}))

                    
                    
                else:
                    send_msg(self._publish_socket, self.mtool.fill_msg("start_mx",
                                                            args=self.mx_args()))

    def mx_args(self):
        return ["run_multiplexer", self.mx_addr,
                '--multiplexer-password', self.mx_pass,
                '--rules', launcher_tools.mx_rules_path()]

    @msg_handlers.handler("launched_process_info")
    def handle_launched_process_info(self, message, sock):
        if message.proc_type == 'multiplexer':
            self._wait_register = len(self.exp_config.peer_machines())
            self.status.peer_status(message.name).set_status(
                                            launcher_tools.RUNNING)
            send_msg(self._publish_socket, self.mtool.fill_msg('start_peers',
                                            mx_data=self.mx_args()))
        elif message.name == 'config_server':
            self.status.peer_status(message.name).set_status(
                                            launcher_tools.RUNNING)
        elif message.proc_type == 'obci_peer':

            self.status.peer_status(message.name).set_status(
                                            launcher_tools.LAUNCHING)
        self.status_changed(self.status.status_name, self.status.details,
            peers={message.name : self.status.peer_status(message.name).status_name})


    @msg_handlers.handler("all_peers_launched")
    def handle_all_peers_launched(self, message, sock):
        if self._exp_extension:
            self._exp_extension = {}
            self.logger.info("all additional peers launched.")
            return

        self._wait_register -= 1
        self.logger.info(str(message) + str(self._wait_register))
        if self._wait_register == 0:
                self.status.set_status(launcher_tools.LAUNCHING)
                self.status_changed(self.status.status_name, self.status.details)
        if not self._kill_and_launch: # if kill/launch, this variable was set in _kill_and_launch_peers()
            self._ready_register = len(self.exp_config.peers) - 2 #without mx and config_server, for now default is 1 mx

    def _choose_process_address(self, proc, addresses):
        self.logger.info("(exp) choosing sv address:" + str(addresses))
        addrs = []
        chosen = None
        if proc.is_local():
            addrs = net.choose_local(addresses)
        if not addrs:
            addrs = net.choose_not_local(addresses)
        if addrs:
            chosen = addrs.pop()
        return chosen

    @msg_handlers.handler('get_experiment_info')
    def handle_get_experiment_info(self, message, sock):
        send_msg(self._publish_socket, self.mtool.fill_msg('rq_ok'))
        send_msg(sock, self.mtool.fill_msg('experiment_info',
                                            experiment_status=self.status.as_dict(),
                                            unsupervised_peers=self.unsupervised_peers,
                                            origin_machine=self.exp_config.origin_machine,
                                            uuid=self.exp_config.uuid,
                                            scenario_dir=self.exp_config.scenario_dir,
                                            peers=self.exp_config.peers_info(),
                                            launch_file_path=self.exp_config.launch_file_path,
                                            name=self.name))

    @msg_handlers.handler('get_peer_info')
    def handle_get_peer_info(self, message, sock):
        if message.peer_id not in self.exp_config.peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                        err_code='peer_id_not_found'))
        else:
            peer_info = self.exp_config.peers[message.peer_id].info(detailed=True)
            send_msg(sock, self.mtool.fill_msg('peer_info', **peer_info))


    @msg_handlers.handler('get_peer_param_values')
    def handle_get_peer_param_values(self, message, sock):
        if message.peer_id not in self.exp_config.peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                        err_code='peer_id_not_found'))
        else:
            peer_id = message.peer_id
            vals = self.exp_config.all_param_values(peer_id)
            send_msg(sock, self.mtool.fill_msg('peer_param_values',
                                        peer_id=peer_id,param_values=vals,
                                        sender=self.uuid))


    @msg_handlers.handler('get_peer_config')
    def handle_get_peer_config(self, message, sock):
        send_msg(sock, self.mtool.fill_msg('ping', sender=self.uuid))

    @msg_handlers.handler('get_experiment_scenario')
    def handle_get_experiment_scenario(self, message, sock):
        jsoned = serialize_scenario_json(self.exp_config)
        send_msg(sock, self.mtool.fill_msg('experiment_scenario', scenario=jsoned))

    @msg_handlers.handler('set_experiment_scenario')
    def handle_set_experiment_scenario(self, message, sock):
        if self.exp_config.peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', err_code='scenario_already_set'))
        else:
            jsonpar = launch_file_parser.LaunchJSONParser(
                        launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
            self.exp_config.launch_file_path = None

            inbuf = io.BytesIO(message.scenario.encode('utf-8'))
            jsonpar.parse(inbuf, self.exp_config)
            print "set experiment scenario...............", message.scenario

            rd, details = self.exp_config.config_ready()
            if rd:
                self.status.set_status(launcher_tools.READY_TO_LAUNCH)
            else:
                self.status.set_status(launcher_tools.NOT_READY, details=details)
                self.logger.warning("scenario not ready %s %s", str(rd), str(details))
            self.exp_config.status(self.status)
            self.launch_file = self.exp_config.launch_file_path = message.launch_file_path
            send_msg(sock, self.mtool.fill_msg('rq_ok'))
            send_msg(self._publish_socket, self.mtool.fill_msg('experiment_scenario',
                                            scenario=message.scenario,
                                            launch_file_path=message.launch_file_path,
                                            uuid=self.uuid))
            send_msg(self.source_req_socket, self.mtool.fill_msg('experiment_info_change', uuid=self.uuid,
                name=self.name, launch_file_path=message.launch_file_path))
            self.poller.poll_recv(self.source_req_socket, timeout=8000)


    @msg_handlers.handler('start_experiment')
    def handle_start_experiment(self, message, sock):
        if not self.status.status_name == launcher_tools.READY_TO_LAUNCH:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                            err_code='exp_status_'+self.status.status_name,
                                            details=self.status.details))
        else:
            self.status.set_status(launcher_tools.LAUNCHING)
            send_msg(sock, self.mtool.fill_msg('starting_experiment',
                            sender=self.uuid))
            self.status_changed(self.status.status_name, self.status.details)
            result, details = self._start_experiment()
            if not result:
                send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
                                     sender=self.uuid, err_code='', details=details))
                self.logger.error("EXPERIMENT LAUNCH ERROR!!!")
                self.status.set_status(launcher_tools.FAILED_LAUNCH, details)
            self.status_changed(self.status.status_name, self.status.details)


    @msg_handlers.handler('join_experiment')
    def handle_join_experiment(self, message, sock):
        if message.peer_id in self.exp_config.peers or \
            message.peer_id in self.unsupervised_peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                    err_code='peer_id_in_use'))
        elif self.mx_addr is None and 'mx' in self.exp_config.peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                    err_code='mx_not_running'))

        elif self.status.status_name != launcher_tools.RUNNING and \
            self.status.status_name != launcher_tools.LAUNCHING:
            # temporary status bug workaround.
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                    err_code='exp_status_'+self.status.status_name,
                                            details=""))
        else:
            self.unsupervised_peers[message.peer_id] = dict(peer_type=message.peer_type,
                                                            path=message.path)
            send_msg(sock, self.mtool.fill_msg('rq_ok', params=dict(mx_addr=self.mx_addr)))

    @msg_handlers.handler('leave_experiment')
    def handle_leave_experiment(self, message, sock):
        if not message.peer_id in self.unsupervised_peers:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
                                    err_code='peer_id_not_found'))
        else:
            del self.unsupervised_peers[message.peer_id]
            send_msg(sock, self.mtool.fill_msg('rq_ok'))

    @msg_handlers.handler('add_peer')
    def handle_add_peer(self, message, sock):
        """Add new peer to existing scenario. It may run on a different machine than 
        already running peers. add_peer works at runtime and before runtime.
        """
        self.logger.info("Handle add peer: "+str(message))
        machine = message.machine or self.origin_machine
        peer_id = message.peer_id
        _launching = None  # state of the (maybe ongoing) launching process 

        if (self.status.status_name in launcher_tools.POST_RUN_STATUSES) or\
            self.status.status_name == launcher_tools.READY_TO_LAUNCH and\
                 self.status.peer_status_exists(launcher_tools.LAUNCHING):
            self.logger.warning("add peer - experiment status incompatible!")
            send_msg(sock, self.mtool.fill_msg('rq_error',  request=message.dict(), 
                err_code='experiment_status_incompatible'))
            return

        if peer_id in self.exp_config.peers:
            self.logger.warning("add peer - peer id in use!")
            send_msg(sock, self.mtool.fill_msg('rq_error',  request=message.dict(), 
                err_code='peer_id_in_use'))
        try:
            self.logger.info("add peer - try extending config...")
            _launching = len(self.supervisors) == len(self.exp_config.peer_machines())
            launch_file_parser.extend_experiment_config(self.exp_config, peer_id,
                message.peer_path, config_sources=message.config_sources, 
                launch_deps=message.launch_dependencies, custom_config_path=message.custom_config_path, 
                param_overwrites=message.param_overwrites,
                machine=machine, apply_globals=message.apply_globals)
        except Exception, e:
            self.logger.warning("add peer - problem with extending config!")
            send_msg(sock, self.mtool.fill_msg('rq_error', details=str(e), request=message.dict(), 
                err_code='problem_with_extending_config'))
            return
        else:
            self.logger.info("add peer - check config valid ...")
            rd, details = self.exp_config.config_ready()
            if rd:
                self.logger.info("add peer - config is valid!")
                # config is valid, we can proceed
                send_msg(sock, self.mtool.fill_msg('rq_ok'))

                self.status.peers_status[peer_id] = launcher_tools.PeerStatus(peer_id, 
                                                    status_name=launcher_tools.READY_TO_LAUNCH)
                                
                ser = PeerConfigSerializerJSON()
                bt = io.BytesIO()
                ser.serialize(self.exp_config.peers[peer_id].config, bt)
                peer_conf = unicode(bt.getvalue())

                # broadcast message about scenario modification
                self.logger.info("add peer - bradcast scenario mods...")
                send_msg(self._publish_socket, self.mtool.fill_msg("new_peer_added", peer_id=peer_id, machine=machine,
                    uuid=self.uuid, status_name=launcher_tools.READY_TO_LAUNCH, config=peer_conf, peer_path=message.peer_path))
            else:
                self.logger.warning("add peer - config invalid!")
                send_msg(sock, self.mtool.fill_msg('rq_error', 
                                    err_code='config_incomplete', details=details, request=message.dict()))
                return

        if self.status.status_name not in launcher_tools.RUN_STATUSES:
            self.logger.info("additional peers will launch along with base scenario")
        else:
            # ...do actual work
            if machine not in self.supervisors and _launching:
                self.logger.info("add peer - start supervisor on machine: "+str(machine))
                self._exp_extension = { machine : [peer_id] }
                self._start_obci_process_supervisors([machine])
            elif not _launching:
                # the peer data will be sent to process supervisor in launch_data, so we do nothing
                self.logger.info("add peer - not _lauching, nothing else to do")
                pass

            elif self.status.peer_status('mx').status_name == launcher_tools.RUNNING:
                # 'start_peers' has been already sent so we additionally request for launching the
                # new peer
                ldata = {}
                ldata[peer_id] = self.exp_config.launch_data(machine)[peer_id]
                self.logger.info("add peer - send start_peers...")
                send_msg(self._publish_socket, self.mtool.fill_msg("start_peers", mx_data=self.mx_args(), 
                                                        add_launch_data={machine : ldata}))
            else:
                self.logger.info("add peer - last else, nothing else to do")
        self.logger.info("add peer - ALL DONE!")

    @msg_handlers.handler("kill_peer")
    def handle_kill_peer(self, message, sock):
        peer_id = message.peer_id
        peer = self.exp_config.peers.get(message.peer_id, None)
        if not peer:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(), 
                err_code="peer_id_not_found"))
            return

        del self.exp_config.peers[peer_id]
        rd, details = self.exp_config.config_ready()
        self.exp_config.peers[peer_id] = peer
        if not rd:
            send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(), 
                err_code="config_dependencies_error", details=details))
            return
        if message.remove_config:
            peer.del_after_stop = True

        send_msg(sock, self.mtool.fill_msg("rq_ok"))
        send_msg(self._publish_socket, self.mtool.fill_msg("_kill_peer", peer_id=peer_id, 
            machine=(peer.machine or self.origin_machine)))


    @msg_handlers.handler("obci_peer_registered")
    def handle_obci_peer_registered(self, message, sock):
        peer_id = message.peer_id
        if not peer_id in self.exp_config.peers:
            self.logger.error("Unknown Peer registered!!! {0}".format(peer_id))
        else:
            self.logger.info("Peer registered!!! {0}".format(peer_id))
            for par, val in message.params.iteritems():
                self.exp_config.update_local_param(peer_id, par, val)
            send_msg(self._publish_socket, self.mtool.fill_msg('obci_control_message',
                                        severity='info', msg_code='obci_peer_registered',
                                        launcher_message=message.dict(),
                                        sender=self.uuid, peer_name=self.name, peer_type=self.peer_type(),
                                        sender_ip=self.origin_machine))

    @msg_handlers.handler("obci_peer_params_changed")
    def handle_obci_peer_params_changed(self, message, sock):
        peer_id = message.peer_id
        if not peer_id in self.exp_config.peers:
            self.logger.error("Unknown Peer update!!! {0}".format(
                                self.name, self.peer_type(), peer_id))
        else:
            self.logger.info("Params changed!!! {0} {1}".format(
                                peer_id, message.params))
            for par, val in message.params.iteritems():
                try:
                    self.exp_config.update_local_param(peer_id, par, val)
                except Exception, e:
                    self.logger.error("Invalid params!!! {0} {1} {2}".format(peer_id,
                                message.params, str(e)))

            send_msg(self._publish_socket, self.mtool.fill_msg('obci_control_message',
                                        severity='info', msg_code='obci_peer_params_changed',
                                        launcher_message=message.dict(),
                                        sender=self.uuid, peer_name=self.name, peer_type=self.peer_type(),
                                        sender_ip=self.origin_machine))



    @msg_handlers.handler("obci_peer_ready")
    def handle_obci_peer_ready(self, message, sock):
        peer_id = message.peer_id
        if not peer_id in self.exp_config.peers:
            self.logger.error("Unknown Peer update!!! {0}".format(peer_id))
            return
        self.status.peer_status(peer_id).set_status(
                                            launcher_tools.RUNNING)
        self._ready_register -= 1
        self.logger.info("{0} peer ready! {1} to go".format(peer_id,
                                self._ready_register))

        if self._ready_register == 0:
            self.status.set_status(launcher_tools.RUNNING)


        self.status_changed(self.status.status_name, self.status.details,
            peers={peer_id : self.status.peer_status(peer_id).status_name})



# {"status": ["failed", null],
# "sender": "fb32da42-c8b6-47db-a958-249cd5e1f366",
# "receiver": "", "sender_ip": "127.0.0.1",
# "path": "/home/administrator/dev/openbci/acquisition/info_saver_peer.py",
# "peer_id": "info_saver", "type": "obci_peer_dead"}

    @msg_handlers.handler('obci_peer_dead')
    def handle_obci_peer_dead(self, message, sock):
        if not message.peer_id in self.exp_config.peers:
            self.logger.error("peer_id" + str(message.peer_id) + "not found!")
            return
        status = message.status[0]
        details = message.status[1]

        self.status.peer_status(message.peer_id).set_status(status, details=details)
        if status == launcher_tools.FAILED:
            send_msg(self._publish_socket,
                        self.mtool.fill_msg("stop_all", receiver=""))
            self.status.set_status(launcher_tools.FAILED,
                                    details='Failed process ' + message.peer_id)
        elif not self.status.peer_status_exists(launcher_tools.RUNNING) and\
                (self.status.status_name not in [launcher_tools.FAILED, launcher_tools.FAILED_LAUNCH]):
            self.status.set_status(status)
        if self.exp_config.peers[message.peer_id].del_after_stop:
            del self.exp_config.peers[message.peer_id]
            self.status.del_peer_status(message.peer_id)
        message.experiment_id = self.uuid
        send_msg(self._publish_socket, message.SerializeToString())
        self.status_changed(self.status.status_name, self.status.details)

    @msg_handlers.handler('obci_launch_failed')
    def handle_obci_launch_failed(self, message, sock):
        if self._exp_extension:
            self.logger.error("launch of additional peers failed")
            self._exp_extension = {}
        pass

    @msg_handlers.handler('launch_error')
    def handle_launch_error(self, message, sock):
        peer_id = message.details["peer_id"]
        if not peer_id in self.exp_config.peers:
            self.logger.error("peer_id" + str(message.peer_id) + "not found!")
            return

        self.status.peer_status(peer_id).set_status(launcher_tools.FAILED_LAUNCH)
        self.status.set_status(launcher_tools.FAILED_LAUNCH,
                                    details='Failed to launch process ' + peer_id)
        message.sender = self.uuid
        send_msg(self._publish_socket, message.SerializeToString())
        self.status_changed(self.status.status_name, self.status.details)


    @msg_handlers.handler('update_peer_config')
    def handle_update_peer_config(self, message, sock):
        if self.status.status_name not in [launcher_tools.NOT_READY, \
                                        launcher_tools.READY_TO_LAUNCH]:
            send_msg(sock, self.mtool.fill_msg('rq_error', err_code='update_not_possible',
                                        details='Experiment status: '+self.status.status_name))
        else:
            conf = dict(local_params=message.local_params,
                        external_params=message.external_params,
                        launch_dependencies=message.launch_dependencies,
                        config_sources=message.config_sources)
            peer_id = message.peer_id

            try:
                self.exp_config.update_peer_config(peer_id, conf)
            except Exception, e:
                send_msg(sock, self.mtool.fill_msg('rq_error', err_code='update_failed',
                                        details=str(e)))
            else:
                send_msg(sock, self.mtool.fill_msg('rq_ok'))


    @msg_handlers.handler("dead_process")
    def handle_dead_process(self, message, sock):
        proc = self.subprocess_mgr.process(message.machine, message.pid)
        if proc is not None:
            proc.mark_delete()
            status, details = proc.status()
            self.logger.warning("Process " + proc.proc_type + "dead:" +\
                             status + str(details) + proc.name + str(proc.pid))
            if proc.proc_type == 'obci_process_supervisor':
                send_msg(self._publish_socket,
                        self.mtool.fill_msg("stop_all", receiver=""))
                self.status.set_status(launcher_tools.FAILED,
                        details='Failed LAUNCHER component obci_process_supervisor')
            elif proc.proc_type == 'obci_experiment':
                pass
            if status == subprocess_monitor.FAILED:
                pass
        self.status_changed(self.status.status_name, self.status.details)


    @msg_handlers.handler('save_scenario')
    def handle_save_scenario(self, message, sock):
        send_msg(sock, self.mtool.fill_msg('rq_error', err_code='action_not_supported'))

    @msg_handlers.handler('nearby_machines')
    def handle_nearby_machines(self, message, sock):
        self._nearby_machines.mass_update(message.nearby_machines)

        self.current_ip = self._nearby_machines.this_addr_network()

        send_msg(self._publish_socket, message.SerializeToString())


    @msg_handlers.handler("experiment_finished")
    def handle_experiment_finished(self, message, sock):
        # [make mx_messsage]
        # [handler in config_server]
        # stop_all
        # status - finished
        pass

    @msg_handlers.handler("morph_to_new_scenario")
    def handle_morph(self, message, sock):
        # FIXME "LAUNCHING" -- msg bug workaround
        if self.status.status_name not in [launcher_tools.RUNNING, launcher_tools.LAUNCHING]:
            self.logger.error("EXPERIMENT STATUS NOT RUNNING, MORPH NOT ALLOWED")
            if sock.getsockopt(zmq.TYPE) in [zmq.REQ, zmq.ROUTER]:
                
                send_msg(sock, self.mtool.fill_msg('rq_error',
                                                        err_code='experiment_not_running',
                                                        details=self.status.details))
            return

        new_launch_file = launcher_tools.obci_root_relative(message.launch_file)
        exp_config, status = self._initialize_experiment_config(new_launch_file,
                                                            message.overwrites)
        self.logger.info("new launch status %s %s", str(exp_config), str(status.status_name))
        if status.status_name != launcher_tools.READY_TO_LAUNCH:
            self.logger.error("NEW SCENARIO NOT READY TO LAUNCH, MOPRH NOT ALLOWED")
            if sock.getsockopt(zmq.TYPE) in [zmq.REQ, zmq.ROUTER]:
                
                send_msg(sock, self.mtool.fill_msg('rq_error',
                                                        err_code='launch_file_invalid',
                                                        details=dict(status_name=status.status_name,
                                                                        details=status.details)))
            return

        valid, details = self._validate_morph_leave_on(self.exp_config, exp_config, message.leave_on)
        self.logger.info("morph valid: %s %s", str(valid), str(details))

        if not valid:
            if sock.getsockopt(zmq.TYPE) in [zmq.REQ, zmq.ROUTER]:
                send_msg(sock, self.mtool.fill_msg('rq_error',
                                                    err_code='leave_on_peers_invalid',
                                                    details=details))
            return

        kill_list, launch_list = self._diff_scenarios(self.exp_config,
                                                        exp_config, message.leave_on)


        self.logger.info("KILL_LIST " + str(kill_list))
        self.logger.info("LAUNCH_LIST" + str(launch_list))

        old_name = self.name
        old_status = self.status
        self.name = message.name if message.name is not None else new_launch_file
        self.launch_file = new_launch_file
        self.status = status

        old_config = self.exp_config
        self.exp_config = exp_config

        for p in message.leave_on:
            self.exp_config.peers[p] = old_config.peers[p]

        if sock.getsockopt(zmq.TYPE) in [zmq.REP, zmq.ROUTER]:
            send_msg(sock, self.mtool.fill_msg('starting_experiment'))
            self.status.set_status(launcher_tools.LAUNCHING)
            send_msg(self.source_req_socket, self.mtool.fill_msg('experiment_transformation',
                            status_name=self.status.status_name, details=self.status.details,
                            uuid=self.uuid, name=self.name, launch_file=new_launch_file,
                            old_name=old_name, old_launch_file=old_config.launch_file_path))
            self.poller.poll_recv(self.source_req_socket, timeout=8000)



        #TODO -- notice obci_server of name/config change

        self._kill_and_launch_peers(kill_list, launch_list, self.exp_config, old_config)
        self._kill_unused_supervisors()

        pst = {}
        for peer in self.status.peers_status:
            if peer not in launch_list and peer not in kill_list:
                self.status.peer_status(peer).set_status(old_status.peer_status(peer).status_name,
                                                old_status.peer_status(peer).details)

                pst[peer] = self.status.peer_status(peer).status_name

        self.status_changed(self.status.status_name, self.status.details,
                        peers=pst)

        # list: to kill, to restart (unless in leave-on)
        # start supervisors if new machnes specified
        # send launch_data to all
        # start
        # deregister / register in obci_server

    def _kill_and_launch_peers(self, kill_list, launch_list, new_config, old_config):
        kill_data = {}
        for peer in kill_list:
            machine = old_config.peers[peer].machine
            if not machine:
                machine = self.origin_machine
            if not machine in kill_data:
                kill_data[machine] = []
            kill_data[machine].append(peer)

        launch_data = {}
        self._ready_register = 0

        for machine in new_config.peer_machines():
            ldata = new_config.launch_data(machine)
            peers = ldata.keys()
            for peer in peers:
                if peer in launch_list:
                    if not machine in launch_data:
                        launch_data[machine] = {}
                    launch_data[machine][peer] = ldata[peer]
                    self._ready_register += 1

        self._kill_and_launch = (kill_data, launch_data)

        new_supervisors = []
        for machine in launch_data:
            if machine not in old_config.peer_machines():
                new_supervisors.append(machine)
        if new_supervisors:
            self._wait_register = len(new_supervisors)

            self._start_obci_process_supervisors(new_supervisors)
#--------------------------------------------------------------------------------------
        for machine in kill_data:
            to_kill = kill_data[machine]
            if machine in launch_data:
                to_launch = launch_data[machine]
            else:
                to_launch = {}
            send_msg(self._publish_socket, self.mtool.fill_msg("manage_peers",
                                                kill_peers=to_kill, start_peers_data=to_launch,
                                                receiver=self.supervisors[machine].uuid))
        for machine in launch_data:
            if machine not in kill_data and machine not in new_supervisors:
                to_kill = []
                to_launch = launch_data[machine]
                send_msg(self._publish_socket, self.mtool.fill_msg("manage_peers",
                                                kill_peers=to_kill, start_peers_data=to_launch,
                                                receiver=self.supervisors[machine].uuid))


    def _kill_unused_supervisors(self):
        pass

    def _diff_scenarios(self, old_config, new_config, leave_on):
        kill_list = []
        for peer in old_config.peers:
            if peer not in new_config.peers:
                kill_list.append(peer)
        launch_list = []
        for peer in new_config.peers:
            if peer not in old_config.peers:
                launch_list.append(peer)

        for peer in new_config.peers:
            if peer in old_config.peers and not peer in leave_on and \
                                        not peer in ['mx', 'config_server']:
                kill_list.append(peer)
                launch_list.append(peer)
        return kill_list, launch_list


    def _validate_morph_leave_on(self, old_config, new_config, leave_on):

        for peer_id in leave_on:

            old_p = old_config.peers.get(peer_id, None)
            new_p = new_config.peers.get(peer_id, None)
            if old_p is None or new_p is None:
                return False, "Peer id " + peer_id + 'present old config: ' \
                                    + str(old_p is not None) + ', present in new config: ' +\
                                    + str(new_p is not None)
            if old_p.path != new_p.path:
                return False, "Peer ids [" + peer_id + "] point to different programs: " +\
                                    "old: " + old_p.path + ', new: ' + new_p.path

            old_machine = old_p.machine if old_p.machine else socket.gethostname()
            new_machine = new_p.machine if new_p.machine else socket.gethostname()

            if old_machine != new_machine:
                return False, "Peer id " + peer_id + 'is to be launched on a different machine: ' +\
                                "old: " + old_machine + ', new:' + new_machine
            else:
                return True, ""


    def cleanup_before_net_shutdown(self, kill_message, sock=None):
        
        send_msg(self._publish_socket,
                        self.mtool.fill_msg("kill", receiver="", sender=self.uuid))
        self.logger.info('sent KILL to supervisors')
        super(OBCIExperiment, self).cleanup_before_net_shutdown(kill_message, sock)

    def clean_up(self):
        self.logger.info("exp cleaning up")
        self.subprocess_mgr.stop_monitoring()
        #self._tcp_srv.shutdown()

    def _handle_register_sv_timeout(self, sv_process):
        txt = "Supervisor for machine {0} FAILED TO REGISTER before timeout".format(
                                                                sv_process.machine_ip)
        self.logger.error(txt)

        sock = self._push_sock(self.ctx, self._push_addr)

        # inform observers about failure
        send_msg(sock, self.mtool.fill_msg("experiment_launch_error",
                                                sender=self.uuid,
                                                err_code="create_supervisor_error",
                                                details=dict(machine=sv_process.machine_ip,
                                                            error=txt)))
        sock.close()

    @msg_handlers.handler("get_tail")
    def handle_get_tail(self, message, sock):
        if self.status.status_name == launcher_tools.RUNNING:
            if not message.peer_id in self.exp_config.peers:
                send_msg(sock, self.mtool.fill_msg("rq_error",
                                            err_code="peer_not_found",
                                            details="No such peer: "+message.peer_id))
                return
            machine = self.exp_config.peer_machine(message.peer_id)
            self.logger.info("getting tail for %s %s", message.peer_id, machine)
            send_msg(self._publish_socket, message.SerializeToString())
            self.client_rq = (message, sock)

    @msg_handlers.handler("tail")
    def handle_tail(self, message, sock):
        if self.client_rq:
            if message.peer_id == self.client_rq[0].peer_id:
                send_msg(self.client_rq[1], message.SerializeToString())


def experiment_arg_parser():
    parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
                    description='Create, launch and manage an OBCI experiment.')
    parser.add_argument('--sv-pub-addresses', nargs='+',
                    help='Addresses of the PUB socket of the supervisor')
    parser.add_argument('--sandbox-dir',
                    help='Directory to store temporary and log files')
    parser.add_argument('--launch-file',
                    help='Experiment launch file')
    parser.add_argument('--name', default='obci_experiment',
                    help='Human readable name of this process')
    parser.add_argument('--launch', default=False,
                       help='Launch the experiment specified in launch file')
    parser.add_argument('--current-ip', help='IP addr of host machine')
    parser.add_argument('--ovr', nargs=argparse.REMAINDER)


    return parser

if __name__ == '__main__':

    args = experiment_arg_parser().parse_args()
    print args
    pack = None
    if args.ovr is not None:
        pack = peer_cmd.peer_overwrites_pack(args.ovr)
    exp = OBCIExperiment(args.sandbox_dir,
                            args.launch_file, args.sv_addresses, args.sv_pub_addresses,
                            args.rep_addresses, args.pub_addresses, args.name,
                            args.current_ip, args.launch, overwrites=pack)

    exp.run()
