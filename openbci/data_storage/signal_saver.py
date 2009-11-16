#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer

import signalml_save_manager
import sys
import settings, variables_pb2
class SignalSaver(BaseMultiplexerServer):
    def __init__(self, addresses, p_session_name, p_path):
        super(SignalSaver, self).__init__(addresses=addresses, type=peers.SIGNAL_SAVER)
        self.start_saving_session(p_session_name, p_path)

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE and self._session_is_active:
            l_vec = variables_pb2.SampleVector()
	    l_vec.ParseFromString(mxmsg.message)
	    for x in l_vec.samples:
                self._save_manager.data_received(x.value)

        elif mxmsg.type == types.SIGNAL_SAVER_CONTROL_MESSAGE:
            print("signal saver control message: "+mxmsg.message)
            if mxmsg.message == 'finish_saving':
                l_files = self.end_saving_session()
                print("Saved files: ")
                print(l_files)
                sys.exit(0)
                
    def start_saving_session(self, p_session_name, p_path="./"):
        self._session_is_active = True
        l_signal_params = {}
        l_sampling_frequency = int(self.conn.query(message = "SamplingRate", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        l_channels_names = self.conn.query(message = "AmplifierChannelsToRecord", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        l_channels_names = l_channels_names.strip().split(' ')
        l_signal_params['number_of_channels'] = len(l_channels_names)
        l_signal_params['sampling_frequency'] = l_sampling_frequency
        l_signal_params['channels_names'] = l_channels_names
        self._save_manager = signalml_save_manager.SignalmlSaveManager(p_session_name, p_path, l_signal_params)

    def end_saving_session(self):
        self._session_is_active = False
        return self._save_manager.finish_saving()
    def sigterm_handler(self, x, y):
        print("sigterm_handler")
        l_files = self.end_saving_session()
        print("Saved files:")
        print (l_files)
        raise JustCatchMeException()

class JustCatchMeException(Exception):
    def __str__(self):
        return "Just catch me!"


import signal, sys
if __name__ == "__main__":
    l_session_name = "random_name"
    l_path = "./"
    try:
        l_path = sys.argv[2]
    except IndexError:
        pass
    try: 
        l_session_name = sys.argv[1]
    except IndexError:
        pass
    print("Start writing... to '"+l_path+l_session_name+"*' files...")
    try:
        l_signal_saver = SignalSaver(settings.MULTIPLEXER_ADDRESSES, l_session_name, l_path)
        #signal.signal(signal.SIGTERM, l_signal_saver.sigterm_handler)
        l_signal_saver.loop()
    except JustCatchMeException, e:
        pass
        
