import ugm_config_manager
import ugm_engine
import candygram as cg
import time
import thread
class UgmTestServer(object):
    def run(self):
        """RUN"""
        for i_conf in self.configs[1:]:
            time.sleep(self.secs)
            self.config_manager.update_from_file(i_conf)
            self.engine.update_or_rebuild()
    def __init__(self):
        print("Run ugm and refresh it from config files defined in 'ugm.configs.ugm_slideshow_config', you can also define slideshow`s speed there.")
        l_config_module = __import__('ugm.configs.ugm_slideshow_config',
                                     fromlist = ['ugm.configs'])
        self.configs = l_config_module.configs
        self.secs = l_config_module.seconds
        self.config_manager = ugm_config_manager.UgmConfigManager(self.configs[0])
        self.engine = ugm_engine.UgmEngine(self.config_manager)
        thread.start_new_thread(self.run, ())
        self.engine.run()

if __name__ == '__main__':
    UgmTestServer()
