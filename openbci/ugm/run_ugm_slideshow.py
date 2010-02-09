import ugm_config_manager
import ugm_engine
import candygram as cg
import time
import thread
class UgmTestServer(object):
    def __init__(self):
        print("Run ugm and refresh it from config files defined in 'ugm.configs.ugm_slideshow_config', you can also define slideshow`s speed there.")
        l_config_module = __import__('ugm.configs.ugm_slideshow_config',
                                     fromlist = ['ugm.configs'])
        l_configs = l_config_module.configs
        l_secs = l_config_module.seconds
        l_config_manager = ugm_config_manager.UgmConfigManager(l_configs[0])
        l_engine = ugm_engine.UgmEngine(l_config_manager)
        l_engine_thread = thread.start_new_thread(l_engine.run, ())
        time.sleep(l_secs)
        for i_conf in l_configs[1:]:
            l_config_manager.update_from_file(i_conf)
            l_engine.update()
            time.sleep(l_secs)
            print("UGM UPDATED")

if __name__ == '__main__':
    UgmTestServer()
