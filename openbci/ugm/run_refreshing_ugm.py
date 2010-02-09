import ugm_config_manager
import ugm_engine
import thread
import time
class UgmTestServer(object):
    def __init__(self):
        print("Ugm has just been displayed. It refreshes from ugm.configs.ugm_config file every 1 second, so feel free to modify the file and inspect results.")
        l_config_manager = ugm_config_manager.UgmConfigManager('ugm.configs.ugm_config')
        l_engine = ugm_engine.UgmEngine(l_config_manager)
        l_engine_thread = thread.start_new_thread(l_engine.run, ())
        while True:
            time.sleep(1)
            l_config_manager.update_from_file()
            l_engine.update()
if __name__ == '__main__':
    UgmTestServer()
