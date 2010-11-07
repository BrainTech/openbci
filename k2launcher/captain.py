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
        "MULTIPLEXER_ADDRESSES": "0.0.0.0:31889",
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
task("./experiment_builder/experiment_manager_ania.py mx-on config", "experiment_manager_ania")
task("sleep 1; ./super_diode_control.py", "diode_control")
task("sleep 1; ./diode_catcher.py", "diode_catcher")
task("sleep 1; ./amplifiers/tmsi_bluetooth_eeg_amplifier.py --bt_addr 00:A0:96:1B:48:DB ", "amplifier")
task("sleep 4; ./filters/svarog_filter.py", "svarog_filter")
task("sleep 1; ./logics/logic_speller.py", "logics")
task("sleep 4; ./analysis/ssvep_analysis.py", "analysis")

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

start("data_storing", "svarog_pinger")
start("data_storing", "hashtable")
start("data_storing", "signal_catcher")
start("data_storing", "signal_streamer")
start("data_storing", "amplifier" )
start("data_storing", "signal_saver")
start("data_storing", "finish_signal_saver")



start("virtual_amplifier", "svarog_pinger")
start("virtual_amplifier", "hashtable")
#start("virtual_amplifier", "signal_catcher")
start("virtual_amplifier", "signal_streamer")
start("virtual_amplifier", "virtual_amplifier" )


#start("pokaz", "hashtable")

start("pokaz", "svarog_pinger")
#start("pokaz", "virtual_amplifier")
start("pokaz", "amplifier")
start("pokaz", "signal_catcher")
start("pokaz", "signal_streamer")
#start("pokaz", "filter")
start("pokaz", "hashtable", priority=10)
start("pokaz", "svarog_filter")
start("pokaz", "diode_catcher")
start("pokaz", "diode_control")
start("pokaz", "ugm")
start("pokaz", "logics")
start("pokaz", "analysis")
#start("pokaz", "logics")

start("add_experiment", "ugm")
start("add_experiment", "diode_control")
start("add_experiment", "tag_catcher")
start("add_experiment", "signal_saver")
start("add_experiment", "experiment_manager")

#start("add_data_storing", "tag_catcher")
start("add_data_storing", "signal_saver")
start("add_data_storing", "signal_saver2")

start("stop_storing", "finish_signal_saver")

start("add_monitor", "monitor")

start("add_spectrum", "spectrum")

start("test_experiment", "svarog_pinger")
start("test_experiment", "hashtable")
start("test_experiment", "svarog_filter")
start("test_experiment", "ugm")
start("test_experiment", "diode_control")
start("test_experiment", "signal_catcher")
start("test_experiment", "signal_streamer")
start("test_experiment", "virtual_amplifier")
start("test_experiment", "tag_catcher")
start("test_experiment", "signal_saver")
start("test_experiment", "experiment_manager")

start("remotely_test_experiment", "svarog_pinger")
start("remotely_test_experiment", "hashtable")
start("remotely_test_experiment", "svarog_filter")
start("remotely_test_experiment", "remote_ugm")
start("remotely_test_experiment", "diode_control")
start("remotely_test_experiment", "signal_catcher")
start("remotely_test_experiment", "signal_streamer")
start("remotely_test_experiment", "virtual_amplifier")
start("remotely_test_experiment", "tag_catcher")
start("remotely_test_experiment", "signal_saver")
start("remotely_test_experiment", "experiment_manager")


start("exp_ani", "svarog_pinger")
start("exp_ani", "hashtable")
start("exp_ani", "svarog_filter")
start("exp_ani", "ugm")
start("exp_ani", "signal_catcher")
start("exp_ani", "signal_streamer")
start("exp_ani", "amplifier")
start("exp_ani", "tag_catcher")
start("exp_ani", "signal_saver")
start("exp_ani", "signal_saver2")
start("exp_ani", "experiment_manager_ania")


start("exp_ani_test", "svarog_pinger")
start("exp_ani_test", "hashtable")
start("exp_ani_test", "svarog_filter")
start("exp_ani_test", "ugm")
start("exp_ani_test", "signal_catcher")
start("exp_ani_test", "signal_streamer")
start("exp_ani_test", "virtual_amplifier")
start("exp_ani_test", "tag_catcher")
start("exp_ani_test", "signal_saver")
start("exp_ani_test", "signal_saver2")
start("exp_ani_test", "experiment_manager_ania")




start("experiment", "svarog_pinger")
start("experiment", "hashtable")
start("experiment", "svarog_filter")
start("experiment", "ugm")
start("experiment", "diode_control")
start("experiment", "signal_catcher")
start("experiment", "signal_streamer")
start("experiment", "amplifier")
start("experiment", "tag_catcher")
start("experiment", "signal_saver")
start("experiment", "experiment_manager")


start("demo1", "svarog_pinger")
start("demo1", "hashtable", priority=10)

start("demo1", "virtual_amplifier")
#start("demo", "virtual_file")
#start("demo", "tmsi_bluetooth_eeg_amplifier")
start("demo1", "svarog_filter")
start("demo2", "signal_catcher")
start("demo2", "signal_streamer")
#start("demo", "filter")
#start("demo", "hashtable", priority=10)
start("demo2", "monitor")



start("demo", "svarog_pinger")
start("demo", "hashtable", priority=10)

start("demo", "virtual_amplifier")
#start("demo", "virtual_file")
#start("demo", "tmsi_bluetooth_eeg_amplifier")
start("demo", "svarog_filter")
start("demo", "signal_catcher")
start("demo", "signal_streamer")
#start("demo", "filter")
#start("demo", "hashtable", priority=10)
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

