import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import  connect_client
from ugm import ugm_config_manager


class TestUgmSender(object):
    def __init__(self):
        self._connection = connect_client(type = peers.LOGIC)
    def run(self):
        l_mgr = ugm_config_manager.UgmConfigManager()
        i = 0
        while True:
            i = i + 1
            print("Type: 0 ugm.tests.some_config to set full update for ugm from some_config.py")
            print("Type 1 ugm.tests.some_config to update config for ugm from some_config.py")
            if i > 1:
                l_input = raw_input()
            else:
                l_input = '0 ugm.configs.test1'
            l_type, l_config = l_input.split(" ")
            l_msg = variables_pb2.UgmUpdate()
            l_msg.type = int(l_type)
            l_mgr.update_from_file(l_config)
            l_msg.value = l_mgr.config_to_message()
            self._connection.send_message(message = l_msg.SerializeToString(), type=types.UGM_UPDATE_MESSAGE, flush=True)
if __name__ == "__main__":
    TestUgmSender().run()
 
