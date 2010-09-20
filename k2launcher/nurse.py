#!/usr/bin/python

import os
import sys
import time
import gflags
import time

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import k2launcher_pb2
from utils import pb2_construct, get_env, convert_host_ports
from nurse_helper import close_screen, start_screen, running_screens


mx_addresses_raw = os.environ.get('MULTIPLEXER_ADDRESSES', None)
assert mx_addresses_raw != None, "No mx addresses given!"
mx_addresses = convert_host_ports(mx_addresses_raw)
mx_password = os.environ.get('MULTIPLEXER_PASSWORD', None)
assert mx_password != None, "No mx password given!"

connection = connect_client(type = peers.K2_LAUNCHER_NURSE)

FLAGS = gflags.FLAGS
gflags.DEFINE_string("node", "BASE", "Name of the node") 

try:
    argv = FLAGS(sys.argv)
except gflags.FlagsError, e:
    print "%s\nUsage: %s ARGS\n%s" % (e, sys.argv[0], FLAGS)
    sys.exit(1)

node_name = FLAGS.node

actions = {
        k2launcher_pb2.Command.START: 'START',
        k2launcher_pb2.Command.RESTART: 'RESTART',
        k2launcher_pb2.Command.KILL: 'KILL'
}

def start_command(command):
    if command.task.pidfile:
        if os.path.exists(command.task.pidfile):
            os.unlink(command.task.pidfile)

    env = get_env(command.task)
    if command.task.expose_pidfile_in_env and command.task.pidfile:
        env['PIDFILE'] = command.task.pidfile

    start_screen(command.task.screen_name, command.task.cmd,
        env=env,
        cwd=command.task.working_dir,
        bash_debug=command.task.bash_debug,
        bash_after=command.task.bash_after,
        date_at_the_beginning=command.task.date_at_the_beginning)

def check_pidfile(pidfile):
    try:
        return os.path.exists("/proc/" + str(file(pidfile, "r").read()))
    except Exception:
        return False

babysitter = {}
# task_id => kind, command, started time
# 1 = pid
# 2 = screen
# 3 = both

while True:
    # babysitter
    running = running_screens([babysitter[task_id][1].task.screen_name for task_id in babysitter.keys()])
    dead = []

    for task_id in babysitter:
        bs, command, start = babysitter[task_id]
        if time.time() - start < command.task.babysit_delay:
            continue
        if (bs > 1 and not command.task.screen_name in running) or \
            (bs != 2 and not check_pidfile(command.task.pidfile)):
            dead.append(command)

    print "Found dead, restarting:", [command.task.task_id for command in dead]

    for command in dead:
        close_screen(command.task.task_id)
        babysitter[command.task.task_id][2] = time.time()
        start_command(command)
        notification = command.SerializeToString()
        connection.send_message(message=notification,
                type=types.K2_LAUNCHER_BABYSITTER_RESTART)

    # new commands
    mxmsg = connection.query(
            message=pb2_construct(k2launcher_pb2.GetNext, node=node_name).SerializeToString(),
            type=types.K2_LAUNCHER_GET_NEXT_REQUEST)
    if not mxmsg.message:
        time.sleep(1)
        continue
    command = k2launcher_pb2.Command()
    command.ParseFromString(mxmsg.message)
    print "DOING", actions[command.type], command.task.task_id, command.task.cmd

    screen_name = command.task.screen_name
    if command.type in [command.KILL, command.RESTART]:
        if command.task.task_id in babysitter:
            del babysitter[command.task.task_id]
        close_screen(screen_name)
    if command.type in [command.START, command.RESTART]:
        bs = 0
        if command.task.babysit_pidfile:
            bs += 1
        if command.task.babysit_screen:
            bs += 2
        if bs:
            babysitter[command.task.task_id] = [bs, command, time.time()]
        start_command(command)

    connection.send_message(message=mxmsg.message,
            type=types.K2_LAUNCHER_COMMAND_DONE)
