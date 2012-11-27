#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq
from PyQt4 import QtCore
import os
import socket
import io
import codecs
import subprocess
import threading
import time

from common.message import send_msg, recv_msg, OBCIMessageTool, PollingObject
from launcher.launcher_messages import message_templates
import launcher.system_config as system_config
import launcher.launch_file_parser as launch_file_parser
import launcher.launcher_tools as launcher_tools
import launcher.subprocess_monitor as subprocess_monitor
import peer.peer_cmd as peer_cmd
import common.net_tools as net
import common.obci_control_settings as settings

MODE_BASIC = 'basic'
MODE_ADVANCED = 'advanced'
MODE_EXPERT = 'expert'
MODES = [MODE_ADVANCED, MODE_BASIC]#, MODE_EXPERT]

DEFAULT_CATEGORY = u'Uncategorised'
USER_CATEGORY = u'User defined'

SIGNAL_STORAGE_PEERS = {
    "signal_saver" : "acquisition/signal_saver_peer.py",
    "tag_saver" : "acquisition/tag_saver_peer.py",
    "info_saver" : "acquisition/info_saver_peer.py"
}
STORAGE_CONTROL = "exps/exps_helper.py"

class ExperimentEngineInfo(QtCore.QObject):
    exp_saver_msg = QtCore.pyqtSignal(object)

    def __init__(self, preset_data=None, launcher_data=None, ctx=None):
        self.preset_data = preset_data
        self.launch_file = None
        self.launcher_data = launcher_data
        self.name = None
        self.info = ""
        self.public_params = []
        self.origin_machine = ''
        self.unsupervised_peers = {}
        self.old_uid = None

        self.ctx = ctx
        self.exp_req = None
        self.mtool = OBCIMessageTool(message_templates)
        self.poller = PollingObject()

        self.category = DEFAULT_CATEGORY

        if preset_data is not None:
            self.setup_from_preset(preset_data)

        elif launcher_data is not None:
            self.setup_from_launcher(launcher_data)
        super(ExperimentEngineInfo, self).__init__()

    def cleanup(self):
        if self.exp_req:
            self.exp_req.close()#linger=0)

    def setup_from_preset(self, preset_data, launcher=False):
        self.preset_data = preset_data
        self.overwrites = {}
        self.runtime_changes = {}

        self.status = launcher_tools.ExperimentStatus()
        self.exp_config = system_config.OBCIExperimentConfig()

        self.name = preset_data['name']
        self.launch_file = preset_data['launch_file']
        self.info = preset_data['info']
        self.public_params = [p.strip() for p in preset_data['public_params'].split(',')]
        self.exp_config.uuid = self.name + '--' + self.launch_file

        self.category = preset_data['category']

        result, details = self._make_config()

        self.status.details = details
        self._set_public_params()

    def _addr_connectable(self, addr, machine):
        return machine == socket.gethostname() or \
                    (net.is_ip(addr) and not net.addr_is_local(addr))

    def setup_from_launcher(self, launcher_data, preset=False, transform=False):
        self.launcher_data = launcher_data
        self.runtime_changes = {}
        if preset:
            self.old_uid = self.exp_config.uuid

        if not preset or transform:
            self.overwrites = {}
            self.status = launcher_tools.ExperimentStatus()
            self.exp_config = system_config.OBCIExperimentConfig()

        self.name = launcher_data['name']# if not preset else self.old_uid
        if not preset:
            self.launch_file = launcher_data['launch_file_path']

        connected = False
        if not transform:
            self.ctx = self.ctx if self.ctx is not None else zmq.Context()
            self.exp_req = self.ctx.socket(zmq.REQ)
            machine = launcher_data['origin_machine']

            for addr in launcher_data['rep_addrs']:
                if self._addr_connectable(addr, machine):
                    try:
                        self.exp_req.connect(addr)
                    except Exception, e:
                        print addr, False
                    else:
                        connected = True
            if not connected:
                print "Connection to experiment ", self.name, "UNSUCCESFUL!!!!!!"
                return

        self.exp_config.uuid = launcher_data['uuid']
        self.exp_config.origin_machine = launcher_data['origin_machine']

        self.exp_config.launch_file_path = self.launch_file
        self.uuid = self.exp_config.uuid

        result, details = self._get_experiment_scenario()
        self.exp_config.status(self.status)
        self.status.set_status(launcher_data['status_name'], details=launcher_data['details'])

        self._get_experiment_details()
        self._set_public_params()


    def _set_public_params(self):
        for par in self.public_params:
            if len(par.split('.')) == 2:
                [peer, param] = par.split('.')
                self.exp_config.peers[peer].public_params.append(param)

    def _make_config(self):

        self.exp_config.launch_file_path = self.launch_file
        self.uuid = self.exp_config.uuid

        result, details = self.make_experiment_config()

        self.exp_config.status(self.status)
        return result, details


    #FIXME  !!! copy-paste from obci_experiment
    def make_experiment_config(self):
        launch_parser = launch_file_parser.LaunchFileParser(
                            launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
        if not self.launch_file:
            return False, "Empty scenario."

        try:
            with open(launcher_tools.expand_path(self.launch_file)) as f:
                launch_parser.parse(f, self.exp_config, apply_globals=True)
        except Exception as e:
            self.status.set_status(launcher_tools.NOT_READY, details=str(e))
            print "config errror   ", str(e)
            return False, str(e)

        rd, details = self.exp_config.config_ready()
        if rd:
            self.status.set_status(launcher_tools.READY_TO_LAUNCH)
        else:
            self.status.set_status(launcher_tools.NOT_READY, details=details)
            print rd, details

        return True, None

    def _get_experiment_scenario(self):
        if not self.exp_req:
            return False, "No experiment socket"
        response = self.comm_exp(self.mtool.fill_msg("get_experiment_scenario"))
        if not response:
            return False, "No response from experient"
        print "GOT SCENARIO", response.scenario

        jsonpar = launch_file_parser.LaunchJSONParser(
                        launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
        inbuf = io.BytesIO(response.scenario.encode('utf-8'))
        jsonpar.parse(inbuf, self.exp_config)
        rd, details = self.exp_config.config_ready()
        if rd:
            self.status.set_status(launcher_tools.READY_TO_LAUNCH)
        else:
            self.status.set_status(launcher_tools.NOT_READY, details=details)
            print rd, details
        return True, None

    def _get_experiment_details(self):
        if not self.exp_req:
            return
        exp_msg = self.comm_exp(self.mtool.fill_msg("get_experiment_info"))
        if not exp_msg:
            return

        self.origin_machine = exp_msg.origin_machine

        for peer, short_info in exp_msg.peers.iteritems():
            # self.exp_config.set_peer_machine(peer, short_info['machine'])

            msg = self.comm_exp(self.mtool.fill_msg("get_peer_info",
                                        peer_id=peer))
            if not msg:
                return

            ext_defs = {}
            for name, defi in msg.external_params.iteritems():
                ext_defs[name] = defi[0] + '.' + defi[1]
            strict_update = os.path.exists(launcher_tools.expand_path(self.launch_file))
            self.exp_config.update_peer_config(peer, dict(config_sources=msg.config_sources,
                                                launch_dependencies=msg.launch_dependencies,
                                                local_params=msg.local_params,
                                                external_params=ext_defs))

        for peer, status in exp_msg.experiment_status['peers_status'].iteritems():
            self.status.peer_status(peer).set_status(
                                            status['status_name'],
                                            details=status['details'])

    def parameters(self, peer_id, mode):
        params = {}
        peer = self.exp_config.peers[peer_id]
        if mode == MODE_BASIC:
            for par in peer.public_params:
                params[par] = (self.exp_config.param_value(peer_id, par), None)
        else:
            params = peer.config.local_params
            for param in peer.config.local_params:
                params[param] = (self.exp_config.param_value(peer_id, param), None)
            for param, defi in peer.config.ext_param_defs.iteritems():
                source_symbol = defi[0]
                source = peer.config.config_sources[source_symbol]
                params[param] = (self.exp_config.param_value(peer_id, param), source+'.'+defi[1])
        return params


    def comm_exp(self, msg):
        send_msg(self.exp_req, msg)
        response, _ = self.poller.poll_recv(self.exp_req, timeout=3000)
        if not response:
            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!1 no response to ", msg
            self.exp_req.close()
            self.exp_req = self.ctx.socket(zmq.REQ)
            for addr in self.launcher_data['rep_addrs']:
                if self._addr_connectable(addr, self.launcher_data['origin_machine']):
                    self.exp_req.connect(addr)
            return None
        return self.mtool.unpack_msg(response)


    def updatable(self, peer_id, config_part, **kwargs):
        return False

    def update_peer_param(self, peer_id, param, value, runtime=False):
        changes = self.overwrites if not runtime else self.runtime_changes

        ovr = changes.get(peer_id, None)
        ovr = ovr if ovr is not None else {}
        if param not in ovr:
            old = self.exp_config.param_value(peer_id, param)
            if old != value:
                ovr[param] = old
                changes[peer_id] = ovr

        self.exp_config.update_local_param(peer_id, param, value)


    def get_launch_args(self):
        d = dict(launch_file=self.launch_file, name=self.name)
        args = ['--ovr']
        if self.overwrites:
            for peer_id in self.overwrites:
                args.append('--peer')
                args.append(peer_id)

                for arg in self.overwrites[peer_id]:
                    args += ['-p', arg, self.exp_config.param_value(peer_id, arg)]
        pack = peer_cmd.peer_overwrites_pack(args)
        d['overwrites'] = pack
        print "overwrites pack!!!!!!!!!!!!!!!!!!!!!  ", pack
        return d

    def peer_info(self, peer_id):
        return self.exp_config.peers[peer_id]

    def add_peer(self, peer_id, peer_path, config_sources=None, launch_deps=None, 
                                             custom_config_path=None, param_overwrites=None,machine=None):

        return launch_file_parser.extend_experiment_config(self.exp_config, peer_id, peer_path,
                     config_sources, launch_deps,
                    custom_config_path, param_overwrites, machine, apply_globals=True)


    def enable_signal_storing(self, store_options):
        if not store_options:
            return

        if int(store_options['append_timestamp']):
            store_options = dict(store_options)
            store_options['save_file_name'] = store_options['save_file_name']+"_"+str(time.time())

        for peer, peer_path in SIGNAL_STORAGE_PEERS.iteritems():
            if peer not in self.exp_config.peers:
                self.add_peer(peer, peer_path)

        saver = self.exp_config.peers['signal_saver']
        params = saver.config.param_values
        for opt, val in store_options.iteritems():
            if opt in saver.config.param_values:
                params[opt] = val

    def stop_storing(self, client):
        client.leave_experiment(self.uuid, "storage_control")
        join_response = client.join_experiment(
                                self.uuid, "storage_control", STORAGE_CONTROL)
        if join_response is None:
            print "connection timeout!"
            return
            
        if not join_response.type == "rq_ok":
            print "join error"
            return
    
        mx_addr = join_response.params["mx_addr"]
        os.environ["MULTIPLEXER_ADDRESSES"] = mx_addr
        pth = os.path.join(launcher_tools.obci_root(), "exps", "exps_helper.py")
        proc = subprocess.Popen(["python", pth, "storage_control"], env=os.environ.copy())

        def check_proc(proc, time_):
            secs = time_
            while proc.returncode is None and secs > 0:
                time.sleep(0.5)
                secs -= 0.5
                proc.poll()
            return proc.returncode

        while proc.returncode is None:
            if check_proc(proc, 5) is None:
                self.exp_saver_msg.emit(proc)
        print ":---)"
        proc.wait()
