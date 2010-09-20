#!/usr/bin/python

import os
import sys
import time
import random
import gflags

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import k2launcher_pb2
from utils import pb2_construct, convert_host_ports, set_env
from nurse_helper import close_screen, start_screen


class Captain(object):
    def __init__(self, mx_addresses=None, mx_password=None, default_env={}, mx_path=""):
        """
        mx_addresses = comma separated list of type
        """
        self.mx_addresses_raw = mx_addresses
        if self.mx_addresses_raw == None:
            self.mx_addresses_raw = default_env.get('MULTIPLEXER_ADDRESSES', None)
        if self.mx_addresses_raw == None:
            self.mx_addresses_raw = os.environ.get('MULTIPLEXER_ADDRESSES', None)
        assert self.mx_addresses_raw != None, "No mx addresses given!"
        self.mx_addresses = convert_host_ports(self.mx_addresses_raw)
        self.mx_password = mx_password
        if self.mx_password == None:
            self.mx_password = default_env.get('MULTIPLEXER_PASSWORD', None)
        if self.mx_password == None:
            self.mx_password = os.environ.get('MULTIPLEXER_PASSWORD', None)
        assert self.mx_password != None, "No mx password given!"
        self.connection = None
        self.default_env = default_env
        self.mx_path = mx_path

    def connect(self):
        self.connection = connect_client(type=peers.K2_LAUNCHER_CAPTAIN,
                addresses=self.mx_addresses, password=self.mx_password)

    def do(self, command, sync=False):
        if not command.id:
            command.id=random.getrandbits(60)
        if not self.connection:
            self.connect()
        mxmsg = self.connection.query(message=command.SerializeToString(),
            type=types.K2_LAUNCHER_COMMAND_REQUEST)
        response = k2launcher_pb2.ScheduleResponse()
        response.ParseFromString(mxmsg.message)
        if response.type == response.OK:
            if sync:
                while True:
                    mxmsg = self.connection.read_message()
                    if mxmsg.type == types.K2_LAUNCHER_COMMAND_DONE:
                        cmd = k2launcher_pb2.Command()
                        cmd.ParseFromString(mxmsg.message)
                        if cmd.id == command.id:
                            break
            return (True, None, None)
        else:
            return (False, response.type, response.message)

    def do_task(self, action, task, sync=False, priority=0, when=0):
        command = pb2_construct(k2launcher_pb2.Command,
            type=action,
            priority=priority,
            when=when)
        if task:
            command.task.CopyFrom(task)
        return self.do(command, sync)

    def do_cmd(self, cmd, task_id, env=None, node=None, **kwargs):
        if env == None:
            env = self.default_env
        task = pb2_construct(k2launcher_pb2.Task, cmd=cmd, node=node,
                task_id=task_id)
        task = set_env(task, env)
        kwargs["task"] = task
        kwargs["action"] = k2launcher_pb2.Command.START
        return self.do_task(**kwargs)

    def init_one_node(self):
        l = self.mx_addresses_raw.split(",")
        for i, x in enumerate(l):
            x = x.strip(" ")
            start_screen("mx_" + str(i), self.mx_path + 'mxcontrol run_multiplexer ' + x + ' --multiplexer-password "' + self.mx_password + '"')
        time.sleep(0.5)
        start_screen("controller", "python controller.py", env=self.default_env)
        time.sleep(0.5)
        start_screen("nurse", "python nurse.py", env=self.default_env)

    def stop_one_node(self):
        self.do_task(k2launcher_pb2.Command.STOP, None, sync=True)
        close_screen("controller")
        close_screen("nurse")

        l = self.mx_addresses_raw.split(",")
        for i, _ in enumerate(l):
            close_screen("mx_" + str(i))

    def check_status(self, task_id):
        get_task_state = pb2_construct(k2launcher_pb2.GetTaskState, task_id=task_id)
        if not self.connection:
            self.connect()
        mxmsg = self.connection.query(message=get_task_state.SerializeToString(),
                type=types.K2_LAUNCHER_GET_TASK_STATE_REQUEST)
        response = mxmsg.message
        print "Task id:", task_id
        if not response:
            print "State: DEAD"
            sys.exit(1)
        else:
            launched_task = k2launcher_pb2.LaunchedTask()
            launched_task.ParseFromString(response)
            if launched_task.state == launched_task.BORN:
                print "State: BORN"
            elif launched_task.state == launched_task.RUNNING:
                print "State: RUNNING"
            print "Restart counter:", launched_task.restart_counter
            print "Launched node:", launched_task.launched_node
            print "Cmd:", launched_task.task.cmd
            print "Screen name:", launched_task.task.screen_name
            print "Babysit pidfile:", launched_task.task.babysit_pidfile
            print "Babysit screen:", launched_task.task.babysit_screen
            print "Pidfile:", launched_task.task.pidfile
            print "Working dir:", launched_task.task.working_dir
            print "Bash debug:", launched_task.task.bash_debug
            print "Bash after:", launched_task.task.bash_after
            print "Date at the beginning:", launched_task.task.date_at_the_beginning
            sys.exit(0)

    def define_flags(self, additional_actions=[], additional_help=""):
        if additional_help:
            additional_help = "\n" + additional_help
        gflags.DEFINE_enum('action', 'help', additional_actions + ['help', 'init_one_node', 'stop_one_node', 'status', 'alias', 'start', 'restart', 'kill'], """Action to be performed. Valid options are:
help = display this help info
init_one_node = launch all needed management stuff on this node
stop_one_node = stop everything on this node
status = get status of task_id
alias = execute defined list of commands
        You have to specify alias_id.
start = start task (given by id or raw command)
        You can start two different things:
            1. Launch predefined task identified by task_id. You can override task_id using override_task_id. You can pass additional options using additional_options.
            2. Launch new command cmd. Name it task_id.
restart = restart task given by id
        You have to specify task_id.
kill = kill task given by id.
        You have to specify task_id""" + additional_help)
        gflags.DEFINE_string('task_id', '', 'Task identification')
        gflags.DEFINE_string('alias_id', '', 'Name of alias list of commands')
        gflags.DEFINE_string('cmd', 0, 'Command to execute')
        gflags.DEFINE_float('priority', 0, 'Priority for command')
        gflags.DEFINE_float('when', 0, 'When command should be launched. when < 0 means now - when, when > 0 means absolute timestamp, when = 0 means now.')
        gflags.DEFINE_string('node', '', 'Where command should be executed (default: empty means anywhere')
        gflags.DEFINE_bool('sync', False, 'Wait till command will be executed')
        gflags.DEFINE_string('override_task_id', '', 'New value to override task_id from factory')
        gflags.DEFINE_string('additional_options', '', 'Options to be appended to command')

    def main(self, callback=None, task_dict=None, alias_dict=None):
        FLAGS = gflags.FLAGS
        self.define_flags()
        try:
            argv = FLAGS(sys.argv)
        except gflags.FlagsError, e:
            print "%s\nUsage: %s ARGS\n%s" % (e, sys.argv[0], FLAGS)
            sys.exit(1)
        if callback:
            if callack(FLAGS):
                return
        if FLAGS.action == 'help':
            print "Usage: %s ARGS\n%s" % (sys.argv[0], FLAGS)
            sys.exit(1)
        if FLAGS.action == 'init_one_node':
            self.init_one_node()
        elif FLAGS.action == 'stop_one_node':
            self.stop_one_node()
        elif FLAGS.action == "status":
            self.check_status(FLAGS.task_id)
        elif FLAGS.action == 'alias':
            for command in alias_dict[FLAGS.alias_id]:
                print self.do(command, FLAGS.sync)
        elif FLAGS.action == 'start':
            if FLAGS.cmd:
                print self.do_cmd(FLAGS.cmd, FLAGS.task_id, sync=FLAGS.sync,
                    priority=FLAGS.priority, when=FLAGS.when)
            else:
                task = task_dict[FLAGS.task_id]
                if FLAGS.additional_options:
                    task.cmd += " " + FLAGS.additional_options
                    if FLAGS.override_task_id:
                        task.task_id = FLAGS.override_task_id
                print self.do_task(k2launcher_pb2.Command.START, task,
                    sync=FLAGS.sync, priority=FLAGS.priority, when=FLAGS.when)
        elif FLAGS.action == 'restart':
            print self.do_task(action=k2launcher_pb2.Command.RESTART, task=pb2_construct(k2launcher_pb2.Task, task_id=FLAGS.task_id),
                    sync=FLAGS.sync, priority=FLAGS.priority, when=FLAGS.when)
        elif FLAGS.action == 'kill':
            print self.do_task(action=k2launcher_pb2.Command.KILL, task=pb2_construct(k2launcher_pb2.Task, task_id=FLAGS.task_id),
                    sync=FLAGS.sync, priority=FLAGS.priority, when=FLAGS.when)


if __name__ == "__main__":
    captain = Captain()
    captain.main()

