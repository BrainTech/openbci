from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import variables_pb2

from data_storage import signal_saver_control
from ugm.ugm_config_manager import UgmConfigManager
import time
INIT_SLEEP = 5
WORD_FILE = 'word'
LONG_FILE = 'long'
SLEEP_FIX = 1
SLEEP_MASK = 0.05
SLEEP_WORD = 0.03
SLEEP_LONG = 5
LOOPS = 10
class Experiment(object):
    def __init__(self):
        self._connection = connect_client(type = peers.LOGIC)
        self._long_mgr = UgmConfigManager()
        self._long_mgr.update_from_file(LONG_FILE, True)
        self._word_mgr = UgmConfigManager()
        self._word_mgr.update_from_file(WORD_FILE, True) 

        self.words = ['mati'+str(i) for i in range(LOOPS)]
        self.fixation = '+'
        self.mask = 'XXXXXXXXXXXXXX'
        self.word_config = {'id':5555, 'message':''}
    def run(self):
        time.sleep(INIT_SLEEP)
        l_saver_control = signal_saver_control.SignalSaverControl()
        l_saver_control.start_saving()
        time.sleep(1)
        for i in range(LOOPS):
            self.send_fixation()
            self.send_mask()
            self.send_word(self.words[i])
            self.send_mask()
            self.send_long_view()
        print("ALL DONE", l_saver_control.finish_saving())
    def send_fixation(self):
        self.word_config['message'] = self.fixation
        self._word_mgr.set_config(self.word_config)
        self.send_to_ugm(self._word_mgr.config_to_message(), 0)
        time.sleep(SLEEP_FIX)
        pass
    def send_mask(self):
        self.word_config['message'] = self.mask
        self.send_to_ugm(str([self.word_config]))
        time.sleep(SLEEP_MASK)
        pass
    def send_word(self, word):
        self.word_config['message'] = word
        self.send_to_ugm(str([self.word_config]))
        time.sleep(SLEEP_WORD)
        pass
    def send_long_view(self):
        self.send_to_ugm(self._long_mgr.config_to_message(), 0)
        time.sleep(SLEEP_LONG)
        pass
    def send_to_ugm(self, config_value, msg_type=1):
        l_type = msg_type
        l_msg = variables_pb2.UgmUpdate()
        l_msg.type = int(l_type)
        l_msg.value = config_value
        self._connection.send_message(
            message = l_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)
        
if __name__ == "__main__":
    Experiment().run()
