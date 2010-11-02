#!/usr/bin/python

import os
import sys



from utils import pb2_construct, set_env
import k2launcher_pb2

home = "/home/mrygacz/openbci/openbci/"
#home = "/home/mati/bci_dev/google_openbci/openbci/"
mx_path = '%sazouk-libraries/build/' % home
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
task("./svarog/pinger.py", "svarog_pinger")
task("./signal_streamer.py", "signal_streamer")
task("./amplifiers/virtual_amplifier.py file ../openbci/data_storage/tests/data/sample_data.obci.info ../openbci/data_storage/tests/data/sample_data.obci.dat ", "virtual_amplifier")
task("./signal_catcher.py", "signal_catcher")
task("./filters/filter.py", "filter")
task("./monitors/monitor.py 0", "monitor")
task("./monitors/spectrum.py 0", "spectrum")

task("./hashtable.py", "hashtable")
task("./ugm/run_ugm.py", "ugm")
task("./ugm/run_ugm.py p300", "p300_ugm")
task("./analysis/p300.py", "p300_analysis")
task("./main_gui.py","gui" )
task("./tag_catcher.py", "tag_catcher")
task("./data_storage/signal_saver.py; sleep 1; ./data_storage/tests/test_manually_signal_saver_control.py start_saving", "signal_saver")
task("./data_storage/tests/test_manually_signal_saver_control.py finish_saving", "finish_saver")
task("./experiment_builder/experiment_manager.py mx-on config", "experiment_manager")
task("./super_diode_control.py", "diode_control")

task("./amplifiers/tmsi_bluetooth_eeg_amplifier.py --bt_addr 00:A0:96:1B:48:DB ", "amplifier")
task("./tags/tests/test_manual_tags_sending.py", "manual_tags_sending")
task("./ugm/tests/test_ugm_sender.py", "manual_ugm_updating")

for task in tasks:
    tasks[task] = set_env(tasks[task], env)

aliases = {}

def start(alias, task_id, **kwargs):
    if not alias in aliases:
        aliases[alias] = []
    aliases[alias].append(pb2_construct(k2launcher_pb2.Command,
        type=k2launcher_pb2.Command.START, task=tasks[task_id], **kwargs))

start("amplifier", "svarog_pinger")
start("amplifier", "hashtable")
start("amplifier", "signal_catcher")
start("amplifier", "signal_streamer")
start("amplifier", "amplifier" )

start("virtual_amplifier", "svarog_pinger")
start("virtual_amplifier", "hashtable")
#start("virtual_amplifier", "signal_catcher")
start("virtual_amplifier", "signal_streamer")
start("virtual_amplifier", "virtual_amplifier" )


start("pokaz", "hashtable")

start("add_experiment", "ugm")
start("add_experiment", "diode_control")
start("add_experiment", "tag_catcher")
start("add_experiment", "signal_saver")
start("add_experiment", "experiment_manager")


start("add_monitor", "monitor")

start("add_spectrum", "spectrum")

start("test_experiment", "svarog_pinger")
start("test_experiment", "hashtable")
start("test_experiment", "ugm")
start("test_experiment", "diode_control")
start("test_experiment", "signal_catcher")
start("test_experiment", "signal_streamer")
start("test_experiment", "filter")
start("test_experiment", "virtual_amplifier")
start("test_experiment", "tag_catcher")
start("test_experiment", "signal_saver")
start("test_experiment", "experiment_manager")



start("experiment", "svarog_pinger")
start("experiment", "hashtable")
start("experiment", "ugm")
start("experiment", "diode_control")
start("experiment", "signal_catcher")
start("experiment", "signal_streamer")
start("experiment", "filter")
start("experiment", "amplifier")
start("experiment", "tag_catcher")
start("experiment", "signal_saver")
start("experiment", "experiment_manager")

start("demo", "virtual_amplifier")
#start("demo", "tmsi_bluetooth_eeg_amplifier")
start("demo", "signal_catcher")
start("demo", "filter")
start("demo", "hashtable", priority=10)
start("demo", "monitor")


start("gui_test", "hashtable")
start("gui_test", "ugm")
start("gui_test", "manual_ugm_updating")

start("gui", "hashtable")
start("gui","ugm")
start("gui", "gui")

start("p300_test", "hashtable")
start("p300_test", "p300_ugm")
start("p300_test", "p300_analysis")


start("svarog_test", "hashtable")
start("svarog_test", "svarog_pinger")
start("svarog_test", "signal_streamer")
start("svarog_test", "amplifier")
start("svarog_test", "manual_tags_sending")

start("svarog_v_test", "hashtable")
start("svarog_v_test", "svarog_pinger")
start("svarog_v_test", "signal_streamer")
start("svarog_v_test", "virtual_amplifier")
start("svarog_v_test", "manual_tags_sending")

start("add_saver", "signal_saver")

start("finish_saver", "finish_saver")


# signal, add_experiment, start_experiment, add_monitor, start_monitor, 


if __name__ == "__main__":
    from captain_helper import Captain
    global_path = os.path.dirname(os.path.normpath(sys.argv[0]))
    captain = Captain(global_path = global_path, default_env=env, mx_path=mx_path)
    captain.main(task_dict=tasks, alias_dict=aliases)

