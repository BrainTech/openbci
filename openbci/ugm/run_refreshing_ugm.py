import ugm_config_manager
import ugm_engine
import candygram as cg
class UgmEngineThread(object):
    def __init__(self, p_engine):
        self._engine = p_engine
    def run(self):
        r = cg.Receiver()
        self._engine.run()
        while True:
            r.receive()
import time
class UgmTestServer(object):
    def __init__(self):
        l_config_manager = ugm_config_manager.UgmConfigManager('ugm_config')
        l_engine = ugm_engine.UgmEngine(l_config_manager)
        l_engine_thread = cg.spawn(UgmEngineThread(l_engine).run)
        while True:
            time.sleep(1)
            l_config_manager.update_from_file()
            l_engine.update()
if __name__ == '__main__':
    UgmTestServer()
