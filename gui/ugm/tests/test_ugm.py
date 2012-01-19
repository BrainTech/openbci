#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ugm import ugm_config_manager
from ugm import ugm_engine
import threading
class UgmTestServer(object):
    def __init__(self, p_config):
        l_config_manager = ugm_config_manager.UgmConfigManager(p_config)
        l_engine = ugm_engine.UgmEngine(l_config_manager)
        l_engine_thread = threading.Thread(target=l_engine.run).start()
        print("You are running ugm with config from ugm_config_for_tests.py")
        while True:
            print("")
            print("Type one of options:")
            print("load - load configuration from file and update ugm")
            print("save - save current ugm config to file")
            print("set - set attribute for ugm element with given id")
            i = raw_input()
            if i == 'load':
                l_config_manager.update_from_file()
                l_engine.update()
                print("DONE!")
            elif i == 'save':
                l_config_manager.update_to_file()
                print("DONE!")
            elif i == 'set':
                print("Type id, attribute_name, attribute_value separated by spaces. Eg: 41 image_path juhu.png")
                i = raw_input().split(' ')
                try:
                    i[2] = int(i[2])
                except:
                    pass

                l_config_manager.set_config_for(int(i[0]),i[1],i[2])
                l_engine.update()
                print("DONE!")
            elif i == 'load_from':
                print("Type module name with ugm config.")
                print("For test you can type: test1, test2, test3, test4")
                i = raw_input()
                l_config_manager.update_from_file(i)
                l_engine.update()
                print("DONE!")

import sys
if __name__ == '__main__':
    try:
        conf = sys.argv[1]
    except:
        conf = 'ugm.tests.ugm_config_for_tests'
    finally:
        UgmTestServer(conf)
