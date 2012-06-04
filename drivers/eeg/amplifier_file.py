#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, sys, Queue
from multiplexer.multiplexer_constants import peers, types
from drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from drivers import drivers_logging as logger
from configs import settings
from launcher.launcher_tools import obci_root
from drivers.eeg import tags_to_mxmsg
from analysis.obci_signal_processing.signal import read_info_source
from analysis.obci_signal_processing.tags import read_tags_source

LOGGER = logger.get_logger("AmplifierFile", "info")

class AmplifierFile(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierFile, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

    def _init_got_configs(self):
        self._init_files()
        self._init_configs()

    def _init_files(self):
        self.f_data = os.path.expanduser(os.path.join(
            self.config.get_param('data_file_dir'), 
            self.config.get_param('data_file_name'))+'.obci.raw')

        i_dir = self.config.get_param('info_file_dir')
        if len(i_dir) == 0:
            i_dir = self.config.get_param('data_file_dir')
        i_name = self.config.get_param('info_file_name')
        if len(i_name) == 0:
            i_name = self.config.get_param('data_file_name')
        self.f_info = os.path.expanduser(os.path.join(i_dir, i_name)+'.obci.xml')

        t_dir = self.config.get_param('tags_file_dir')
        if len(t_dir) == 0:
            t_dir = self.config.get_param('data_file_dir')
        t_name = self.config.get_param('tags_file_name')
        if len(t_name) == 0:
            t_name = self.config.get_param('data_file_name')
        self.f_tags = os.path.expanduser(os.path.join(t_dir, t_name)+'.obci.tag')
        
    def _init_configs(self):
        mgr = read_info_source.FileInfoSource(self.f_info)

        names = mgr.get_param('channels_names')
        type = mgr.get_param('sample_type')
        self.all_types = ';'.join([type]*len(names))
        self.all_names = ';'.join(names)
        self.all_gains = ';'.join(mgr.get_param('channels_gains'))
        self.all_offsets = ';'.join(mgr.get_param('channels_offsets'))

        self.config.set_param('sample_type', mgr.get_param('sample_type'))
        self.config.set_param('sampling_rate', mgr.get_param('sampling_frequency'))
        self.config.set_param('channel_names', self.all_names)
        if len(self.config.get_param('active_channels')) == 0:
            self.config.set_param('active_channels', self.config.get_param('channel_names'))

        #active_names = self.config.get_param('active_channels').split(';')
        #active_gains = []
        #active_offsets = []

        #for ch_name in active_names:
        #    active_gains.append(all_gains[all_names.index(ch_name)])
        #    active_offsets.append(all_offsets[all_names.index(ch_name)])

        #self.config.set_param('channel_gains', ';'.join(active_gains))
        #self.config.set_param('channel_offsets', ';'.join(active_offsets))

    def get_run_args(self,multiplexer_address):
        args = super(AmplifierFile, self).get_run_args(multiplexer_address)

        args.extend(
            ['-f', self.f_data,
             '-t', self.all_types,
             '-n', self.all_names,
             '-g', self.all_gains,
             '-o', self.all_offsets,
             '-s', str(int(float(self.get_param('sampling_rate'))))
              ])
        LOGGER.info("Extended arguments: "+str(args))
        return args

    def set_driver_params(self):
        super(AmplifierFile, self).set_driver_params()
        self.set_tags()

    def set_tags(self):
        tags = read_tags_source.FileTagsSource(self.f_tags).get_tags()
        self.msg_mgr = tags_to_mxmsg.TagsToMxmsg(tags, self.config.get_param('tags_rules'))
        tss = ';'.join([repr(t['start_timestamp']) for t in tags])
        self._communicate("tags_start", timeout_s=0.1, timeout_error=False)
        LOGGER.info("Start sending tss to driver...")
        self._communicate(tss, timeout_s=0.1, timeout_error=False)
        LOGGER.info("Finished sending tss to driver!")
        self._communicate("tags_end", timeout_s=0.1, timeout_error=False)

    def got_trigger(self, ts):
        """Got trigger from the drivers.
        Let`s send next tag (or other message)
        with ts as its realtime timestamp"""
        #...
        tp, msg = self.msg_mgr.next_message(ts)
        if tp is None:
            LOGGER.warning("No tags left but got trigger. Should not happen!!!")
        else:
            LOGGER.info("Send msg of type: "+str(tp))
            self.conn.send_message(
                message = msg,
                type=tp,
                flush=True)

    def do_sampling(self):
        LOGGER.info("Stat waiting on drivers output...")
        while True:
            try:
                v = self.driver_out_q.get_nowait()
                try:
                    ts = float(v)
                except ValueError:
                    if v.startswith('start OK'):
                        LOGGER.info("Driver finished!!!")
                        break
                    else:
                        LOGGER.warning("Got unrecognised message from driver: "+v)
                else:
                    self.got_trigger(ts)

            except Queue.Empty:
                pass

        sys.exit(self.driver.returncode)

if __name__ == "__main__":
    srv = AmplifierFile(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
