import ugm_config_manager
import ugm_engine
import thread
import time
class UgmTestServer(object):
    def run(self):
        """Run."""
        while True:
            time.sleep(1)
            self.config_manager.update_from_file()
            if self.config_manager.old_new_fields_differ():
                self.engine.rebuild()
            else:
                self.engine.update()
        
    def __init__(self):
        print("Ugm has just been displayed. It refreshes from ugm.configs.ugm_config file every 1 second, so feel free to modify the file and inspect results.")
        self.config_manager = ugm_config_manager.UgmConfigManager('ugm.configs.ugm_config')
        self.engine = ugm_engine.UgmEngine(self.config_manager)
        thread.start_new_thread(self.run, ())
        self.engine.run()
if __name__ == '__main__':
    UgmTestServer()
