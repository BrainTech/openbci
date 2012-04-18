#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
import zmq
import threading
import ConfigParser
import codecs
import os
import socket
import uuid

import common.net_tools as net
from common.message import send_msg, recv_msg, OBCIMessageTool, PollingObject

from launcher.launcher_messages import message_templates
import launcher.obci_script as obci_script
import launcher.launcher_tools as launcher_tools
from launcher.launch_file_serializer import LaunchFileSerializerINI

from experiment_engine_info import ExperimentEngineInfo, MODE_ADVANCED, MODE_BASIC,\
DEFAULT_CATEGORY, USER_CATEGORY

import common.obci_control_settings as settings

PRESETS = 'obci_control/gui/presets.ini'

USER_PRESETS = os.path.join(settings.OBCI_HOME_DIR, 'user_presets.ini')

class OBCILauncherEngine(QtCore.QObject):
    update_ui = QtCore.pyqtSignal(object)
    obci_state_change = QtCore.pyqtSignal(object)
    rq_error = QtCore.pyqtSignal(object)

    internal_msg_templates = {
        '_launcher_engine_msg' : dict(task='', pub_addr=''),
        '_user_set_scenario' : dict(uuid='')
    }


    def __init__(self, obci_client, server_ip=None):
        super(OBCILauncherEngine, self).__init__()

        self.server_ip = server_ip
        self.client = obci_client
        self.ctx = obci_client.ctx

        self.mtool = self.client.mtool
        self.mtool.add_templates(self.internal_msg_templates)

        self._cached_nearby_machines = {}

        self.preset_path = os.path.join(launcher_tools.obci_root(), PRESETS)
        self.user_preset_path = USER_PRESETS

        self.experiments = self.prepare_experiments()

        self.obci_poller = zmq.Poller()

        self.monitor_push = self.ctx.socket(zmq.PUSH)
        self.monitor_addr = 'inproc://obci_monitor' + str(uuid.uuid4())[:4]
        self.monitor_push.bind(self.monitor_addr)

        self._stop_monitoring = False
        srv_addr = 'tcp://'+server_ip+':'+net.server_pub_port() if server_ip else None
        self.obci_monitor_thr = threading.Thread(target=self.obci_monitor,
                                                args=[self.ctx, self.monitor_addr,
                                                srv_addr])
        self.obci_monitor_thr.daemon = True
        self.obci_monitor_thr.start()

        self.obci_state_change.connect(self.handle_obci_state_change)

        for exp in self.experiments:
            if exp.launcher_data is not None:
                self._exp_connect(exp.launcher_data)

        self.details_mode = MODE_ADVANCED

    def cleanup(self):
        print "CLEANUP!!!!"
        self._stop_monitoring = True

        self.monitor_push.close()#linger=0)
        for exp in self.experiments:
            exp.cleanup()
        self.experiments = []
        self.obci_monitor_thr.join()

    def exp_ids(self):
        ids = {}
        for i, e in enumerate(self.experiments):
            ids[e.uuid] = i
        return ids

    def index_of(self, exp_uuid):
        if exp_uuid in self.exp_ids():
            return self.exp_ids()[exp_uuid]
        else:
            return None

    def prepare_experiments(self):
        experiments = []
        presets = self._parse_presets(self.preset_path)
        if os.path.exists(self.user_preset_path):
            presets += self._parse_presets(self.user_preset_path, cat_name=USER_CATEGORY)

        for preset in presets:
            exp = ExperimentEngineInfo(preset_data=preset, ctx=self.ctx)
            experiments.append(exp)

        running = self._list_experiments()
        for exp in running:
            matches = [(i, e) for i, e in enumerate(experiments) if\
                        e.launch_file == exp['launch_file_path'] and e.preset_data is not None\
                        and e.status.status_name == launcher_tools.READY_TO_LAUNCH]
            if matches:
                index, preset = matches.pop()
                preset.setup_from_launcher(exp, preset=True)
            else:
                experiments.append(ExperimentEngineInfo(launcher_data=exp, ctx=self.ctx))

        return experiments

    def _addr_connectable(self, addr, machine):
        return machine == socket.gethostname() or \
                    (net.is_ip(addr) and not net.addr_is_local(addr))


    def _exp_connect(self, exp_data):
        for addr in exp_data['pub_addrs']:
            if not addr.startswith('tcp://localhost') and self._addr_connectable(addr, exp_data['origin_machine']):
                send_msg(self.monitor_push, self.mtool.fill_msg('_launcher_engine_msg',
                                                task='connect', pub_addr=addr))

    def _parse_presets(self, preset_path, cat_name=None):
        preset_file = codecs.open(preset_path, encoding='utf-8')
        parser = ConfigParser.RawConfigParser()
        parser.readfp(preset_file)
        presets = []
        for sec in parser.sections():
            pres = {'name' : sec}
            for opt in parser.options(sec):
                pres[opt] = parser.get(sec, opt)
            if not 'category' in pres:
                pres['category'] = cat_name if cat_name is not None else DEFAULT_CATEGORY
            if not 'public_params' in pres:
                pres['public_params'] = ''
            presets.append(pres)
        return presets


    def obci_monitor(self, ctx, pull_addr, server_ip=None):
        pull = ctx.socket(zmq.PULL)
        pull.connect(pull_addr)

        subscriber = ctx.socket(zmq.SUB)
        subscriber.setsockopt(zmq.SUBSCRIBE, "")

        poller = zmq.Poller()
        poller.register(pull, zmq.POLLIN)
        poller.register(subscriber, zmq.POLLIN)

        _all = [pull, subscriber]

        if server_ip:
            addr = server_ip
        else:
            addr = net.server_address(sock_type='pub')
        subscriber.connect(addr)

        def handle_msg(msg):
            if msg.type == '_launcher_engine_msg':
                if msg.task == 'connect':
                    print "msg.pub.addr  ", msg.pub_addr, msg
                    subscriber.connect(msg.pub_addr)
            else:
                self.obci_state_change.emit(msg)

        while not self._stop_monitoring:
            try:
                socks = dict(poller.poll(timeout=200))
            except:
                break

            for socket in socks:
                if  socks[socket] == zmq.POLLIN:
                    msg = self.mtool.unpack_msg(recv_msg(socket))
                    if not self._stop_monitoring:
                        handle_msg(msg)

        for sock in _all:
            sock.close()#linger=0)
        print "monitoring thr finished!"

    def handle_obci_state_change(self, launcher_message):
        type_ = launcher_message.type
        handled = True
        if type_ == 'experiment_created':
            self._handle_experiment_created(launcher_message)

        elif type_ == 'launcher_shutdown':
            self._handle_launcher_shutdown(launcher_message)

        elif type_ == 'kill_sent':
            self._handle_kill_sent(launcher_message)

        elif type_ == 'kill':
            self._handle_kill(launcher_message)

        elif type_ == 'obci_control_message': #obci_peer_registered, obci_peer_params_changed
            self._handle_obci_control_message(launcher_message)

        elif type_ == 'experiment_status_change':
            self._handle_experiment_status_change(launcher_message)

        elif type_ == 'obci_peer_dead':
            self._handle_obci_peer_dead(launcher_message)

        elif type_ == 'experiment_transformation':
            self._handle_experiment_transformation(launcher_message)
        elif type_ == 'nearby_machines':
            self._handle_nearby_machines(launcher_message)
        else:
            handled = False

        if handled:
            self.update_ui.emit(launcher_message)
            print "----engine signalled", type_

    def _handle_experiment_created(self, msg, exp_list=None):
        exps = exp_list if exp_list else self.experiments

        matches = [(i, e) for i, e in enumerate(exps) if\
                        (e.name == msg.name or e.launch_file == msg.launch_file_path) and\
                            e.preset_data is not None]

        if matches:
            index, exp = matches.pop()
            exp.setup_from_launcher(msg.dict(), preset=True)
            print "^^^^^^^^  created exp, UUID:", exp.exp_config.uuid
        else:
            exps.append(ExperimentEngineInfo(launcher_data=msg.dict(), ctx=self.ctx))

        self._exp_connect(msg.dict())

    def _handle_experiment_transformation(self, msg):
        exps = self.experiments
        old_index, old_exp = None, None
        new_index, new_exp = None, None
        print msg

        old_matches = [(i, e) for i, e in enumerate(exps) if\
                (e.launch_file == msg.old_launch_file) ]#and\
                #    e.preset_data is not None]

        print "old_matches", old_matches

        if old_matches:
            old_index, old_exp = old_matches.pop()

        new_matches = [(i, e) for i, e in enumerate(exps) if\
                (e.name == msg.name or e.launch_file == msg.launch_file) and\
                    e.preset_data is not None and e.status.status_name != launcher_tools.RUNNING]
        print "new matches", new_matches

        if new_matches:
            new_index, new_exp = new_matches.pop()

        if old_index is not None:
            print "old match", old_index, old_exp.preset_data
            exp = ExperimentEngineInfo(preset_data=old_exp.preset_data, ctx=self.ctx)
            self.experiments[old_index] = exp

        old_exp.launcher_data['name'] = msg.name
        old_exp.launcher_data['launch_file_path'] = msg.launch_file
        old_exp.launcher_data['status_name'] = msg.status_name
        old_exp.launcher_data['details'] = msg.details
        old_exp.setup_from_launcher(old_exp.launcher_data,
                                                preset=(new_index is not None),
                                                transform=True)

        if new_index is not None:
            old_exp.name = msg.name if msg.name else self.experiments[new_index].name
            old_exp.preset_data = self.experiments[new_index].preset_data
            self.experiments[new_index] = old_exp
        else:
            old_exp.preset_data = None
            self.experiments.append(old_exp)


    def _handle_launcher_shutdown(self, msg):
        self.experiments = []
        presets = self._parse_presets(self.preset_path)
        for preset in presets:
            exp = ExperimentEngineInfo(preset_data=preset, ctx=self.ctx)
            self.experiments.append(exp)

    def _handle_kill_sent(self, msg):
        uid = msg.experiment_id
        index = self.index_of(uid)
        if index is not None:
            print "msg", msg, "uid", uid, "index", index
            exp = self.experiments[index]

            if exp.preset_data:
                exp.setup_from_preset(exp.preset_data)
                exp.launcher_data = None
            else:
                del self.experiments[index]


    def _handle_kill(self, msg):
        pass

    def _handle_obci_control_message(self, msg):
        uid = msg.sender
        index = self.index_of(uid)
        if index is not None:
            exp = self.experiments[index]

            if msg.msg_code in ["obci_peer_registered", "obci_peer_params_changed"]:
                for par, val in msg.launcher_message['params'].iteritems():
                    exp.update_peer_param(msg.launcher_message['peer_id'],
                                            par,
                                            val,
                                            runtime=True)

    def _handle_experiment_status_change(self, msg):
        uid = msg.uuid
        index = self.index_of(uid)
        if index is not None:
            exp = self.experiments[index]
            exp.status.set_status(msg.status_name, msg.details)
            if msg.peers:
                for peer, status in msg.peers.iteritems():
                    exp.status.peer_status(peer).set_status(status)

    def _handle_obci_peer_dead(self, msg):
        uid = msg.experiment_id
        index = self.index_of(uid)
        if index is not None:
            exp = self.experiments[index]

            status_name = msg.status[0]
            details = msg.status[1]
            st = exp.status
            st.peer_status(msg.peer_id).set_status(status_name, details)

    def _handle_nearby_machines(self, msg):
        self._cached_nearby_machines = msg.nearby_machines

    def list_experiments(self):
        return self.experiments

    def _list_experiments(self):
        exp_list = self.client.send_list_experiments()
        exps = []
        if exp_list is not None:
            for exp_data in exp_list.exp_data.values():
                exps.append(exp_data)
        return exps

    def reset_launcher(self, msg):

        self.client.srv_kill()
        running = obci_script.server_process_running()
        if running:
            print "reset_launcher: something went wrong... SERVER STILL RUNNING"

        self.client = obci_script.client_server_prep()
        self.experiments = self.prepare_experiments()

    def stop_experiment(self, msg):
        uid = str(msg)
        index = self.index_of(uid)
        if index is None:
            print "experiment uuid not found: ", uid
            return
        exp = self.experiments[index]
        if not exp.launcher_data:
            print "this exp is not running...", uid
            return
        self._process_response(self.client.kill_exp(exp.uuid))

    def start_experiment(self, msg):
        print "START EXPERIMENT!!!!"
        uid = str(msg)
        index = self.index_of(uid)
        if index is None:
            print "experiment uuid not found: ", uid
            return
        exp = self.experiments[index]
        if exp.launcher_data:
            print "already running"
            return

        args = exp.get_launch_args()
        print "launch_args", args
        result = self.client.launch(**args)

        self._process_response(result)

    def nearby_machines(self):
        nearby_machines = {}
        if not self._cached_nearby_machines:
            res = self.client.send_list_nearby_machines()
            if res is not None:
                self._cached_nearby_machines = res.nearby_machines
        for mach in self._cached_nearby_machines.values():
            nearby_machines[mach["ip"]] = mach["hostname"]
        return nearby_machines

    def save_scenario_as(self, filename_and_experiment):
        filename, exp = filename_and_experiment
        filename = str(filename)
        confdir = os.path.splitext(filename)[0] + "_configs"
        ser = LaunchFileSerializerINI()
        with codecs.open(filename, "w", "utf-8") as f:
            ser.serialize(exp.exp_config, confdir, f)
        new_exp = self._update_experiments(filename, replace=True)
        strmsg = self.mtool.fill_msg("_user_set_scenario", uuid=new_exp.exp_config.uuid)
        self.update_ui.emit(self.mtool.unpack_msg(strmsg))

    def _update_experiments(self, scenario_path, replace=False):
        scenario_path = str(scenario_path)
        preset_data = self._create_preset_data(scenario_path)
        dup = self._find_duplicate(preset_data)
        if dup is not None:
            if not replace:
                preset_data["name"] += "_*"
            else:
                self.experiments.remove(dup)
        exp = ExperimentEngineInfo(preset_data=preset_data, ctx=self.ctx)
        self.experiments.append(exp)
        self._update_user_presets()
        return exp

    def _find_duplicate(self, preset_data):
        dup = None
        for exp in self.experiments:
            if exp.preset_data["name"] == preset_data["name"] and\
                    exp.preset_data["launch_file"] == preset_data["launch_file"] and\
                    exp.preset_data["category"] == preset_data["category"]:
                dup = exp
                break
        return dup

    def _create_preset_data(self, scenario_path):
        name = os.path.basename(scenario_path)
        name = os.path.splitext(name)[0].replace("_", " ")
        data = {"name" : name}
        data["info"] = "User preset"
        if scenario_path.startswith(os.environ['HOME']):
            scenario_path = scenario_path.replace(os.environ['HOME'], '~')
        data["launch_file"] = scenario_path
        data["public_params"] = ""
        data["category"] = USER_CATEGORY
        return data

    def remove_preset(self, experiment):
        self.experiments.remove(experiment)
        self._update_user_presets()
        self.update_ui.emit(None)

    def import_scenario(self, filename):
        new_exp = self._update_experiments(filename)
        strmsg = self.mtool.fill_msg("_user_set_scenario", uuid=new_exp.exp_config.uuid)
        self.update_ui.emit(self.mtool.unpack_msg(strmsg))

    def _update_user_presets(self):
        user_presets = []
        for exp in self.experiments:
            if exp.preset_data is not None:
                if exp.preset_data['category'] == USER_CATEGORY:
                    user_presets.append(exp.preset_data)
        self._save_presets(user_presets, self.user_preset_path)

    def _save_presets(self, preset_list, preset_path):
        parser = ConfigParser.RawConfigParser()
        for pre in preset_list:
            parser.add_section(pre["name"])
            for key in ["info", "launch_file", "public_params", "category"]:
                parser.set(pre["name"], key, pre[key])
        with codecs.open(preset_path, "w", "utf-8") as f:
            parser.write(f)

    def _process_response(self, response):
        if response.type == "rq_error":
            self.rq_error.emit(response)
