#!/usr/bin/python

import os
import sys



from utils import pb2_construct, set_env
import k2launcher_pb2

home = ''.join([os.path.split(
    os.path.realpath(os.path.dirname(__file__)))[0], '/'])

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

multitasks = {}
def multitask(task_ids, task_id):
    multitasks[task_id] = task_ids

task("../svarog/pinger.py", "svarog_pinger")
task("./signal_streamer.py", "signal_streamer")
task("./signal_catcher.py", "signal_catcher")
task("./fast_signal_catcher.py", "fast_signal_catcher")
task("./filters/filter.py", "filter")
task("./monitors/monitor.py 0", "monitor")
task("./monitors/spectrum.py 0", "spectrum")

task("./hashtable.py", "hashtable")
task("./ugm/run_ugm.py", "ugm")
task("./ugm/run_ugm.py p300_train", "p300_ugm_train")
task("./ugm/run_ugm.py p300_test", "p300_ugm_test")
task("./analysis/p300.py", "p300_analysis")
task("./blink_catcher.py", "blink_catcher")
task("./logics/logic_speller.py p300_speller_config", "p300_logics")

task("./main_gui.py","gui" )
task("./tag_catcher.py", "tag_catcher")
task("./data_storage/tests/test_manually_signal_saver_control.py finish_saving", "finish_saver")
task("./data_storage/tests/test_manually_signal_saver_control.py", "manual_saver_control")

task("./experiment_builder/experiment_manager.py mx-on", "experiment_manager")
task("sleep 20; ./experiment_builder/experiment_manager_ania.py mx-on config", "experiment_manager_ania")
task("sleep 1; ./super_diode_control.py", "diode_control")
task("sleep 1; ./diode_catcher.py", "diode_catcher")

task("./amplifiers/tmsi_bluetooth_eeg_amplifier.py --bt_addr 00:A0:96:1B:48:DB", "python_bt_amplifier")
task("./amplifiers/c_tmsi_amplifier/tmsi_server", "c++_usb_amplifier")
task("./amplifiers/c_tmsi_amplifier/tmsi_server -b 00:A0:96:1B:48:DB", "c++_bt_amplifier")
task("./amplifiers/c_tmsi_amplifier/tmsi_server -b 00:A0:96:1B:42:DC", "c++_bt_mobimini_amplifier")
task("./amplifiers/c_tmsi_amplifier/tmsi_server -b 00:A0:96:1B:42:DC", "py_bt_mobimini_amplifier")
task("python ./amplifiers/virtual_amplifier.py file", "virtual_amplifier")
task("python ./amplifiers/virtual_amplifier.py function", "virtual_f_amplifier")
task("python ./amplifiers/virtual_amplifier.py fast", "fast_virtual_amplifier")

task("sleep 4; ./filters/svarog_filter.py", "svarog_filter")
task("sleep 1; ./logics/logic_speller.py", "logics")
task("sleep 4; ./analysis/ssvep_analysis.py", "analysis")

task("./tags/tests/test_manual_tags_sending.py", "manual_tags_sending")
task("./ugm/tests/test_ugm_sender.py", "manual_ugm_updating")
task("./tests/auto_trigger_test.py -p /dev/ttyUSB0 -n 50 -s 1.0 -b 3.0 -t yes -f yes", "auto_trigger")


task("./data_storage/info_saver.py","info_saver")
task("./data_storage/signal_saver.py", "data_saver")
task("./tags/tag_saver.py","tag_saver")
multitask(["info_saver", "data_saver", "tag_saver"], "signal_saver")



task("python ./p300dawida/rysowanie.py", "rysowanie")
task("python ./p300dawida/rysowanie_debug.py", "rysowanie_debug")
task("python ./p300dawida/p300.py", "p300dawid")
task("python ./p300dawida/plotting.py", "plottingdawid")


for task in tasks:
    tasks[task] = set_env(tasks[task], env)

aliases = {}

def start(alias, task_id, **kwargs):
    if not alias in aliases:
        aliases[alias] = []

    task_ids = multitasks.get(task_id, [task_id])
    for i_task_id in task_ids:
        aliases[alias].append(pb2_construct(k2launcher_pb2.Command,
                                            type=k2launcher_pb2.Command.START, 
                                            task=tasks[i_task_id], **kwargs))



start("virtual_p300", "hashtable")
start("virtual_p300", "signal_catcher")
start("virtual_p300", "diode_control")
start("virtual_p300", "diode_catcher")
start("virtual_p300", "virtual_f_amplifier" )
start("virtual_p300", "p300dawid" )
start("virtual_p300", "ugm")
start("virtual_p300", "logics")
#start("virtual_p300", "plottingdawid" )


start("save_test", "hashtable")
start("save_test", "info_saver")
start("save_test", "data_saver")
start("save_test", "tag_saver")
start("save_test", "manual_tags_sending")
start("save_test", "manual_saver_control")
start("save_test", "fast_virtual_amplifier")


start("add_saver", "signal_saver")
start("finish_saver", "finish_saver")
start("add_svarog", "svarog_pinger")

start("virtual_amplifier", "svarog_pinger")
start("virtual_amplifier", "hashtable")
#start("virtual_amplifier", "signal_catcher")
start("virtual_amplifier", "signal_streamer")
start("virtual_amplifier", "virtual_amplifier" )


#start("pokaz", "hashtable")

start("pokaz", "svarog_pinger")
#start("pokaz", "virtual_amplifier")
start("pokaz", "python_bt_amplifier")
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


start("pokaz-data-storing", "svarog_pinger")
start("pokaz-data-storing", "hashtable", priority=10)
start("pokaz-data-storing", "c++_usb_amplifier")
start("pokaz-data-storing", "signal_saver")

start("pokaz-add-special-effects", "diode_catcher")
start("pokaz-add-special-effects", "diode_control")
start("pokaz-add-special-effects", "ugm")
start("pokaz-add-special-effects", "experiment_manager")


start("add_experiment", "ugm")
start("add_experiment", "diode_control")
start("add_experiment", "tag_catcher")
start("add_experiment", "signal_saver")
start("add_experiment", "experiment_manager")

#start("add_data_storing", "tag_catcher")
start("add_data_storing", "signal_saver")

start("stop_storing", "finish_saver")

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


start("exp_ani1", "svarog_pinger")
start("exp_ani1", "hashtable")
start("exp_ani2", "ugm")
#start("exp_ani1", "signal_streamer")
start("exp_ani1", "c++_usb_amplifier")
#start("exp_ani", "python_bt_amplifier")
start("exp_ani2", "tag_catcher")
start("exp_ani2", "signal_saver")
start("exp_ani2", "experiment_manager_ania")

start("exp_ani", "svarog_pinger")
start("exp_ani", "hashtable")
start("exp_ani", "ugm")
#start("exp_ani1", "signal_streamer")
start("exp_ani", "c++_usb_amplifier")
#start("exp_ani", "python_bt_amplifier")
start("exp_ani", "tag_catcher")
start("exp_ani", "signal_saver")
start("exp_ani", "experiment_manager_ania")

start("exp_kamila", "svarog_pinger")
start("exp_kamila", "hashtable")
start("exp_kamila", "c++_usb_amplifier")
#start("exp_ani", "python_bt_amplifier")
start("exp_kamila", "tag_catcher")
start("exp_kamila", "signal_saver")


start("exp_ani_test", "svarog_pinger")
start("exp_ani_test", "hashtable")
start("exp_ani_test", "svarog_filter")
start("exp_ani_test", "ugm")
start("exp_ani_test", "signal_catcher")
start("exp_ani_test", "signal_streamer")
start("exp_ani_test", "virtual_amplifier")
start("exp_ani_test", "tag_catcher")
start("exp_ani_test", "signal_saver")

start("exp_ani_test", "experiment_manager_ania")




start("experiment", "svarog_pinger")
start("experiment", "hashtable")
start("experiment", "ugm")
start("experiment", "diode_control")
start("experiment", "c++_usb_amplifier")
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
#start("demo", "svarog_filter")
start("demo", "signal_catcher")
#start("demo", "signal_streamer")
#start("demo", "filter")
#start("demo", "hashtable", priority=10)
start("demo", "monitor")


start("gui_test", "hashtable")
start("gui_test", "ugm")
start("gui_test", "manual_ugm_updating")

start("gui", "hashtable")
start("gui","ugm")
start("gui", "gui")

start("p300_train_test", "hashtable")
start("p300_train_test", "p300_ugm_train")
start("p300_train_test", "p300_analysis")


start("p300_test_test", "hashtable")
start("p300_test_test", "virtual_f_amplifier")
start("p300_test_test", "fast_signal_catcher")
start("p300_test_test", "p300_ugm_test")
start("p300_test_test", "blink_catcher")
start("p300_test_test", "p300_analysis")
start("p300_test_test", "p300_logics")



start("p300_training", "hashtable")
start("p300_training", "svarog_pinger")
start("p300_training", "c++_usb_amplifier")
start("p300_training", "p300_ugm_train")


start("p300_testing", "hashtable")
start("p300_testing", "svarog_pinger")
start("p300_testing", "c++_usb_amplifier")
start("p300_testing", "p300_ugm_test")




start("svarog_test_py_bt", "hashtable")
start("svarog_test_py_bt", "svarog_pinger")
start("svarog_test_py_bt", "python_bt_amplifier")
start("svarog_test_py_bt", "manual_tags_sending")

start("svarog_test_c++_bt", "hashtable")
start("svarog_test_c++_bt", "svarog_pinger")
start("svarog_test_c++_bt", "c++_bt_amplifier")
start("svarog_test_c++_bt", "manual_tags_sending")

start("svarog_test_c++_bt_mobi", "hashtable")
start("svarog_test_c++_bt_mobi", "svarog_pinger")
start("svarog_test_c++_bt_mobi", "c++_bt_mobimini_amplifier")
start("svarog_test_c++_bt_mobi", "manual_tags_sending")

start("svarog_test_py_bt_mobi", "hashtable")
start("svarog_test_py_bt_mobi", "svarog_pinger")
start("svarog_test_py_bt_mobi", "py_bt_mobimini_amplifier")
start("svarog_test_py_bt_mobi", "manual_tags_sending")

start("svarog_test_c++_usb", "hashtable")
start("svarog_test_c++_usb", "svarog_pinger")
start("svarog_test_c++_usb", "c++_usb_amplifier")
start("svarog_test_c++_usb", "manual_tags_sending")

start("svarog_v_test", "hashtable")
start("svarog_v_test", "svarog_pinger")
start("svarog_v_test", "virtual_amplifier")
start("svarog_v_test", "manual_tags_sending")

start("svarog_f_test", "hashtable")
start("svarog_f_test", "svarog_pinger")
start("svarog_f_test", "virtual_f_amplifier")
start("svarog_f_test", "manual_tags_sending")


start("auto_trigger_f", "hashtable")
start("auto_trigger_f", "virtual_f_amplifier")
start("auto_trigger_f", "signal_saver")
start("auto_trigger_f", "auto_trigger")


start("auto_trigger_v", "hashtable")
start("auto_trigger_v", "virtual_amplifier")
start("auto_trigger_v", "signal_saver")
start("auto_trigger_v", "auto_trigger")

start("auto_trigger_py_bt", "hashtable")
start("auto_trigger_py_bt", "python_bt_amplifier")
start("auto_trigger_py_bt", "signal_saver")
start("auto_trigger_py_bt", "auto_trigger")

start("auto_trigger_c++_bt", "hashtable")
start("auto_trigger_c++_bt", "c++_bt_amplifier")
start("auto_trigger_c++_bt", "signal_saver")
start("auto_trigger_c++_bt", "auto_trigger")

start("auto_trigger_c++_usb", "hashtable")
start("auto_trigger_c++_usb", "c++_usb_amplifier")
start("auto_trigger_c++_usb", "signal_saver")
start("auto_trigger_c++_usb", "auto_trigger")


start("auto_trigger_py_bt_no_storing", "hashtable")
start("auto_trigger_py_bt_no_storing", "python_bt_amplifier")
start("auto_trigger_py_bt_no_storing", "auto_trigger")

start("auto_trigger_c++_bt_no_storing", "hashtable")
start("auto_trigger_c++_bt_no_storing", "c++_bt_amplifier")
start("auto_trigger_c++_bt_no_storing", "auto_trigger")

start("auto_trigger_c++_usb_no_storing", "hashtable")
start("auto_trigger_c++_usb_no_storing", "c++_usb_amplifier")
start("auto_trigger_c++_usb_no_storing", "auto_trigger")


if __name__ == "__main__":
    from captain_helper import Captain
    global_path = os.path.dirname(os.path.normpath(sys.argv[0]))
    captain = Captain(global_path = global_path, default_env=env, mx_path=mx_path)
    captain.main(task_dict=tasks, alias_dict=aliases)

