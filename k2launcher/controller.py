#!/usr/bin/python

import sys
import os
import random
import time

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

from utils import pb2_construct, convert_host_ports, make_screen_name
import k2launcher_pb2


class Controller(BaseMultiplexerServer):
    _any_node = k2launcher_pb2.Task().node 

    def __init__(self, addresses, password):
        self._waiting = []  # list of waiting commands
        self._ready = []  # list of ready commands
        self._launched = {}  # task id => launched task
        self._stop = None  # are we stopping everything? stopping Command

        super(Controller, self).__init__(addresses=addresses, password=password,
                type=peers.K2_LAUNCHER_CONTROLLER)

    def _scan_waiting(self):
        now = time.time()
        for i in xrange(len(self._waiting) - 1, -1, -1):
            command = self._waiting[i]
            if command.when < now:
                self._ready.append(command)
                self._sort()
                del self._waiting[i]

    def _sort(self):
        self._ready.sort(key=lambda command: -command.priority)

    def get_next(self, node):
        self._scan_waiting()
        for i, command in enumerate(self._ready):
            if command.task.node in [node, self._any_node]:
                if command.type == command.START:
                    self._launched[command.task.task_id] = pb2_construct(     
                        k2launcher_pb2.LaunchedTask, task=command.task,
                        launched_node=node,
                        state=k2launcher_pb2.LaunchedTask.BORN)
                elif command.type in [command.RESTART, command.KILL]:
                    if command.task.task_id in self._launched:
                        command.task.node = self._launched[command.task.task_id].launched_node
                        command.task.screen_name = self._launched[command.task.task_id].task.screen_name
                        if command.type == command.RESTART and not command.task.cmd:
                            command.task.CopyFrom(self._launched[command.task.task_id].task)
                    else:
                        continue
                else:
                    assert False, "Unsupported command type"
                del self._ready[i]
                return command
        return None

    def schedule(self, command):
        if command.type == command.STOP:
            self._waiting = []
            self._ready = []
            for task_id in self._launched:
                kill = pb2_construct(k2launcher_pb2.Command, task= \
                        pb2_construct(k2launcher_pb2.Task, task_id=task_id,
                            node=self._launched[task_id].launched_node),
                        type=k2launcher_pb2.Command.KILL,
                        id=random.getrandbits(60))
                self._ready.append(kill)
            self._stop = command
        else:
            if command.type == command.START:
                if not command.task:
                    return pb2_construct(k2launcher_pb2.ScheduleResponse,
                        type=k2launcher_pb2.ScheduleResponse.ERROR_TASK_NOT_SPECIFIED,
                        message="command.task required")
                if command.task.generate_pidfile:
                    command.task.pidfile = "/tmp/pidfile_" + command.task.task_id + ".pid"
                if not command.task.cmd:
                    return pb2_construct(k2launcher_pb2.ScheduleResponse,
                        type=k2launcher_pb2.ScheduleResponse.ERROR_NOT_ENOUGH_ARGUMENTS,
                        message="command.task.cmd required")
                if command.task.babysit_pidfile and not command.task.pidfile: 
                    return pb2_construct(k2launcher_pb2.ScheduleResponse,
                        type=k2launcher_pb2.ScheduleResponse.ERROR_BAD_BABYSITTER,
                        message="cannot babysit by pidfile if not pidfile specified")
                if command.task.babysit_screen and command.task.bash_after:
                    return pb2_construct(k2launcher_pb2.ScheduleResponse,
                        type=k2launcher_pb2.ScheduleResponse.ERROR_BAD_BABYSITTER,
                        message="cannot babysit by screen if bash should be launched after")

            command.task.screen_name = command.task.screen_name or make_screen_name(command.task.task_id)
            command.task.node = command.task.node or self._any_node

            if command.when:
                if command.when < 0:
                    command.when = time.time() - command.when
                self._waiting.append(command)
            else:
                self._ready.append(command)
                self._sort()

        return pb2_construct(k2launcher_pb2.ScheduleResponse,
                    type=k2launcher_pb2.ScheduleResponse.OK)

    
    def try_bye(self):
        if self._stop and not len(self._launched):
            self.conn.send_message(message=self._stop.SerializeToString(),
                    type=types.K2_LAUNCHER_COMMAND_DONE)
            print "Bye!"
            sys.exit(1)
        
    def handle_message(self, mxmsg):
        self.try_bye()
        if mxmsg.type == types.K2_LAUNCHER_GET_NEXT_REQUEST:
            get_next = k2launcher_pb2.GetNext()
            get_next.ParseFromString(mxmsg.message)
            response = self.get_next(get_next.node)
            if response:
                response = response.SerializeToString()
            else:
                response = ""
            self.send_message(message=response,
                    type=types.K2_LAUNCHER_GET_NEXT_RESPONSE)
        
        elif mxmsg.type == types.K2_LAUNCHER_COMMAND_REQUEST:
            command = k2launcher_pb2.Command()
            command.ParseFromString(mxmsg.message)
            response = self.schedule(command).SerializeToString()
            self.send_message(message=response,
                    type=types.K2_LAUNCHER_COMMAND_RESPONSE)
        
        elif mxmsg.type == types.K2_LAUNCHER_COMMAND_DONE:
            command = k2launcher_pb2.Command()
            command.ParseFromString(mxmsg.message)
            if command.type in [command.START, command.RESTART]:
                self._launched[command.task.task_id].state = \
                        k2launcher_pb2.LaunchedTask.RUNNING
                self._launched[command.task.task_id].restart_counter = 0
            elif command.type == command.KILL:
                if command.task.task_id in self._launched:
                    del self._launched[command.task.task_id]
            else:
                assert False, "Unsupported command type"
            self.no_response()

        elif mxmsg.type == types.K2_LAUNCHER_BABYSITTER_RESTART:
            command = k2launcher_pb2.Command()
            command.ParseFromString(mxmsg.message)
            if command.type == command.START and \
                    command.task.task_id in self._launched:
                self._launched[command.task.task_id].restart_counter += 1
            self.no_response()

        elif mxmsg.type == types.K2_LAUNCHER_GET_TASK_STATE_REQUEST:
            get_task_state = k2launcher_pb2.GetTaskState()
            get_task_state.ParseFromString(mxmsg.message)
            task_id = get_task_state.task_id
            if not task_id in self._launched:
                response = ""
            else:
                response = self._launched[task_id].SerializeToString()
            self.send_message(message=response,
                    type=types.K2_LAUNCHER_GET_TASK_STATE_RESPONSE)

        else:
            assert False, "Unsupported message type"

if __name__ == "__main__":
    mx_addresses_raw = os.environ.get('MULTIPLEXER_ADDRESSES', None)
    assert mx_addresses_raw != None, "No mx addresses given!"
    mx_addresses = convert_host_ports(mx_addresses_raw)
    mx_password = os.environ.get('MULTIPLEXER_PASSWORD', None)
    assert mx_password != None, "No mx password given!"

    Controller(addresses=mx_addresses, password=mx_password).loop()
