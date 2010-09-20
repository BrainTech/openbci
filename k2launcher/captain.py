#!/usr/bin/python

import os
import sys

from utils import pb2_construct, set_env
import k2launcher_pb2

home = "./"

mx_path = '%smultiplexer/build/' % home
obci_path = '%sopenbci/' % home

env = os.environ.copy()

_env = {
        "MULTIPLEXER_ADDRESSES": "127.0.0.1:31889",
        "MULTIPLEXER_PASSWORD": "",
        "PYTHONPATH": obci_path + ":" + obci_path + "../:" + mx_path
}

env.update(_env)

for x in env["PYTHONPATH"].split(":"):
    sys.path.insert(1, x)

tasks = {}

def task(cmd, task_id, **kwargs):
    tasks[task_id] = pb2_construct(k2launcher_pb2.Task,
            cmd=cmd, task_id=task_id, working_dir=obci_path, **kwargs)

task("./amplifiers/virtual_amplifier.py", "virtual_amplifier")
task("./signal_catcher.py", "signal_catcher")
task("./filters/filter.py", "filter")
task("./monitors/monitor.py 0", "monitor")
task("./hashtable.py", "hashtable")
#task("python amplifiers/tmsi_bluetooth_eeg_amplifier.py --scan", "tmsi_bluetooth_eeg_amplifier")

for task in tasks:
    tasks[task] = set_env(tasks[task], env)

aliases = {}

def start(alias, task_id, **kwargs):
    if not alias in aliases:
        aliases[alias] = []
    aliases[alias].append(pb2_construct(k2launcher_pb2.Command,
        type=k2launcher_pb2.Command.START, task=tasks[task_id], **kwargs))

start("demo", "virtual_amplifier")
#start("demo", "tmsi_bluetooth_eeg_amplifier")
start("demo", "signal_catcher")
start("demo", "filter")
start("demo", "hashtable", priority=10)
start("demo", "monitor")

if __name__ == "__main__":
    from captain_helper import Captain
    captain = Captain(default_env=env, mx_path=mx_path)
    captain.main(task_dict=tasks, alias_dict=aliases)

