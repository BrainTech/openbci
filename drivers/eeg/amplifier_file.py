#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, os.path, sys
from multiplexer.multiplexer_constants import peers, types
from drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from drivers import drivers_logging as logger
from configs import settings
from launcher.launcher_tools import obci_root
from drivers.eeg import tags_to_mxmsg
from analysis.obci_signal_processing.signal import read_info_source

LOGGER = logger.get_logger("AmplifierFile", "info")

class AmplifierFile(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierFile, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

    def _init_got_configs(self):
        self.f_data = os.path.expanduser(os.path.join(
            self.config.get_param('data_file_dir'), 
            self.config.get_param('data_file_name'))+'.obci.raw')

        i_dir = self.config.get_param('info_file_dir')
        if len(i_dir) == 0:
            i_dir = self.config.get_param('data_file_dir')
        i_name = self.config.get_param('info_file_name')
        if len(i_name) == 0:
            i_name = self.config.get_param('data_file_name')
        f_info = os.path.expanduser(os.path.join(i_dir, i_name)+'.obci.xml')

        t_dir = self.config.get_param('tags_file_dir')
        if len(t_dir) == 0:
            t_dir = self.config.get_param('data_file_dir')
        t_name = self.config.get_param('tags_file_name')
        if len(t_name) == 0:
            t_name = self.config.get_param('data_file_name')
        self.f_tags = os.path.expanduser(os.path.join(t_dir, t_name)+'.obci.tag')
        
        mgr = read_info_source.FileInfoSource(f_info)
        self.config.set_param('sample_type', mgr.get_param('sample_type'))
        self.config.set_param('sampling_rate', mgr.get_param('sampling_freqency'))
        self.config.set_param('channels_names', ';'.join(mgr.get_param('channels_names')))

    def get_run_args(self,multiplexer_address):
        args = super(AmplifierFile, self).get_run_args(multiplexer_address)
        type = self.config.get_param('sample_type').lower()
        args.extend(
            ['-f', self.f_data,
             '-t', type
              ])
        return args

    def set_driver_params(self):
        super(AmplifierFile, self).set_driver_params()
        self.set_tags()

    def set_tags(self):
        tags = read_tags_source.FileTagsSource(self.f_tags).get_tags()
        self.msg_mgr = tags_to_mxmsg.TagsToMxmsg(tags, self.configs.get_param('tags_rules'))
        tss = ';'.join([float(t['start_timestamp']) for t in tags])
        self._communicate("tags_start")
        self._communicate(tss)
        self._communicate("tags_end")

    def got_trigger(self, ts):
        """Got trigger from the drivers.
        Let`s send next tag (or other message)
        with ts as its realtime timestamp"""
        #...
        tp, msg = self.msg_mgr.next_message(ts)
        if tp is None:
            LOGGER.warning("No tags left but got trigger. Should not happen!!!")
        else:
            self.conn.send_message(
                message = msg,
                type=tp,
                flush=True)

    #def do_sampling(self):
    #    
    #    sys.exit(self.driver.returncode)

if __name__ == "__main__":
    srv = AmplifierFile(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
